import functools
import os
import sys
import asyncio
import subprocess
import json
import random

from timeit import default_timer
from aiohttp import (
    ClientSession,
    ClientTimeout,
    ClientError,
    ClientResponse
)

from ..logger.logger import Logger
from .utils import output_reader, flatten

from .base import Agent

DEFAULT_INTERNAL_HOST = os.getenv("INTERNAL_HOST") or "127.0.0.1"
DEFAULT_EXTERNAL_HOST = os.getenv("EXTERNAL_HOST") or "localhost"

PYTHON = os.getenv("PYTHON", sys.executable)
START_TIMEOUT = 60.0

class AriesAgent(Agent):

    def __init__(
        self, 
        http_port: str,
        admin_port: str,
        identity: str = None,
        label: str = None,
        internal_host : str = None,
        external_host : str = None,
        webhook_url: str = None,
        genesis_url: str = None,
        public_did: bool = False,
        public_did_ledger: str = None,
        seed: str = "random",
        wallet_type: str = "indy",
        wallet_name: str = None,
        wallet_key: str = None,
        auto_accept_invites : bool = False,
        plugins: list = []
    ):
        self.identity = identity or 'Acapy Agent'
        self.http_port = http_port
        self.internal_host = internal_host or DEFAULT_INTERNAL_HOST
        self.external_host = external_host or DEFAULT_EXTERNAL_HOST
        self.endpoint = f'http://{self.external_host}:{http_port}'
        self.admin_port = admin_port
        self.admin_url = f"http://{self.internal_host}:{self.admin_port}"
        self.label = label or self.identity
        self.client_session : ClientSession = ClientSession()
        self.proc = None
        self.genesis_url = genesis_url
        self.public_did = public_did
        self.public_did_ledger = public_did_ledger
        self.webhook_url = webhook_url
        self.auto_accept_invites = auto_accept_invites

        rand_name = str(random.randint(100_000, 999_999))
        self.seed = (
            ("default_seed_000000000000000000000000" + rand_name)[-32:]
            if seed == "random"
            else seed
        )

        self.wallet_type = wallet_type
        self.wallet_name = (
            wallet_name or self.identity.lower().replace(" ", "") + rand_name
        )
        self.wallet_key = wallet_key or self.identity + rand_name

        self.plugins = plugins or []

    async def start(self):
        Logger.info("Starting Agent ...")
        
        try:
            if self.public_did:
                await self.register_did()

            await self.__start_process(wait=True)
            Logger.info("Agent Started")
            
        except Exception as e:
            Logger.error(str(e))
            Logger.error("Fail to start agent")
            sys.exit(1)

    async def register_did(self, ledger_url: str = None, role: str = "TRUST_ANCHOR",): 

        ledger_url = ledger_url or self.public_did_ledger

        if not ledger_url:
            raise Exception("No ledger to publish the did")

        Logger.info(f'Registering a new DID on the ledger at {ledger_url} ...')

        data = {
            "alias": self.identity,
            "seed": self.seed,
            "role": role
        }

        try:
            async with self.client_session.post(ledger_url + "/register", json=data) as resp:
                if resp.status != 200:
                    raise Exception(f"Error registering DID, response code {resp.status}.")
                nym_info = await resp.json()
                self.did = nym_info["did"]

            Logger.info(f"DID {self.did} registered for agent.")
            os.environ.putenv('PUBLIC_DID', f'did:sov:{self.did}') 
            os.environ.putenv('PUBLIC_DID_RESOLVER_URL', f'{self.admin_url}/resolver/resolve') 

        except Exception:
            raise Exception(f'Error registering DID. Cannot connect to {ledger_url}')


    async def __start_process(self, wait: bool = True):
        my_env = os.environ.copy()
        process_args = self.__get_process_args()
        Logger.info(process_args)

        # start agent sub-process
        loop = asyncio.get_event_loop()
        self.proc = await loop.run_in_executor(None, self.__process, process_args, my_env, loop)

        if wait:
            await asyncio.sleep(1.0)
            await self.__detect_process()

    def __get_process_args(self):
        return list(
            flatten(
                ([PYTHON, "-m", "aries_cloudagent", "start"], self.__get_agent_args())
            )
        )

    def __get_agent_args(self):
        result = [
            ("--label", self.label),
            ("--endpoint", self.endpoint),
            ("--inbound-transport", "http", "0.0.0.0", str(self.http_port)),
            ("--outbound-transport", "http"),
            ("--admin", "0.0.0.0", str(self.admin_port)),
            "--admin-insecure-mode",
            ("--wallet-type", self.wallet_type),
            ("--wallet-name", self.wallet_name),
            ("--wallet-key", self.wallet_key), 
            "--auto-provision"
        ]

        if self.genesis_url:
            result.append(("--genesis-url", self.genesis_url))
        else:
            result.append("--no-ledger")

        if self.genesis_url and self.public_did:
            result.append(('--seed', self.seed))

        if self.webhook_url:
            result.append(("--webhook-url", self.webhook_url))

        if self.auto_accept_invites:
            result.append("--auto-accept-invites")

        for plugin in self.plugins:
            result.append(("--plugin", plugin))

        result.append(("--plugin", "data_webhooks_protocol"))

        return result

    def __process(self, args, env, loop):
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            env=env, 
            encoding="utf-8"
        )

        loop.run_in_executor(
            None,
            output_reader,
            proc.stdout,
            functools.partial(self.__handle_output)
        )

        loop.run_in_executor(
            None,
            output_reader,
            proc.stderr,
            functools.partial(self.__handle_output)
        )

        return proc

    def __handle_output(self, *output):
        print(*output)

    async def __detect_process(self, headers=None):
        async def fetch_status(url: str, timeout: float, headers = None):
            code = None
            text = None
            start = default_timer()
            async with ClientSession(timeout=ClientTimeout(total=3.0)) as session:
                while default_timer() - start < timeout:
                    try:
                        async with session.get(url, headers=headers) as resp:
                            code = resp.status
                            if code == 200:
                                text = await resp.text()
                                break
                    except (ClientError, asyncio.TimeoutError):
                        pass
                    await asyncio.sleep(0.5)
            return code,text

        status_url = f'{self.admin_url}/status'
        status_code, status_text = await fetch_status(
            status_url, START_TIMEOUT, headers=headers
        )

        if not status_text:
              raise Exception(
                f"Timed out waiting for agent process to start (status={status_code}). "
                + f"Admin URL: {status_url}"
            )

        ok = False
        try:
            status = json.loads(status_text)
            ok = isinstance(status, dict) and "version" in status
        except json.JSONDecodeError:
            pass
        if not ok:
            raise Exception(
                f"Unexpected response from agent process. Admin URL: {status_url}"
            )

    async def stop(self):
        Logger.info(f'Stopping agent...')
        
        await self.client_session.close()
        
        loop = asyncio.get_event_loop()
        if self.proc:
            future = loop.run_in_executor(None, self.__stop_process)
            await asyncio.wait_for(future, 10, loop=loop)
        
        Logger.info(f'Agent Stopped.')
    
    def __stop_process(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                msg = "Process did not terminate in time"
                Logger.info(msg)
                raise Exception(msg)


    async def __admin_request(
        self, method, path, data=None, text=False, params=None, headers=None
    ) -> ClientResponse :
        response = await self.__request(method, self.admin_url + path, data=data, params=params, headers=headers)
        return response

    async def __request(
        self, 
        method, 
        url, 
        data=None, 
        text= False, 
        params=None, 
        headers=None
    ) -> ClientResponse:

        params = {k: v for (k, v) in (params or {}).items() if v is not None }
        async with self.client_session.request(method, url, json=data, params=params, headers=headers) as resp:
            resp_text = await resp.text() 
            try:
                resp.raise_for_status()
            except Exception as e:
                raise Exception(f"Error: {resp.text}") from e

            if not resp_text and not text:
                return None
            if not text:
                try: 
                    return json.loads(resp_text)
                except json.JSONDecodeError as e:
                    raise Exception(f"Error decoding JSON: {resp.text}") from e

            return resp_text
            


