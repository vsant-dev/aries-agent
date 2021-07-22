import asyncio
import os
import argparse

from lib.agent.aries import AriesAgent

async def main(args):
    agent = AriesAgent(
        args['http_port'],
        args['admin_port'],
        identity = args['identity'],
        label= args['label'],
        external_host = args['external_host'],
        webhook_url= args['webhook_url'],
        genesis_url= args['genesis_url'],
        public_did= args['public_did'],
        public_did_ledger= args['public_did_ledger'],
        seed= 'random',
        auto_accept_invites = args['auto_accept_invites'],
        plugins=args['plugins']
    )
    await agent.start()

    try:
        keep_running()

    except KeyboardInterrupt:
        await agent.stop()
        os._exit(1)

def keep_running():
    while True:
        pass

def get_args():
    parse = argparse.ArgumentParser(description="Run Agent")

    parse.add_argument(
        "-id",
        "--identity",
        type=str,
        metavar=("<identity>"),
        help="Agent identity"
    )

    parse.add_argument(
        "-l",
        "--label",
        type=str,
        metavar=("<label>"),
        help="Agent label"
    )


    parse.add_argument(
        "-p",
        "--port",
        type=int,
        metavar=("<port>"),
        help="Choose the agent's endpoint port number to listen on"
    )

    parse.add_argument(
        "-ap",
        "--admin-port",
        type=int,
        metavar=("<admin-port>"),
        help="Choose the agent's admin page port number to listen on"
    )

    parse.add_argument(
        "-g",
        "--genesis-url",
        type=str,
        metavar=("<genesis-url>"),
        help="Url to fetch genesis transactions"
    )

    parse.add_argument(
        "--public-did",
        type=bool,
        const=True,
        nargs="?",
        metavar=("<public-did>"),
        help="""Publish the did on a public ledger. When define this 
            property, you must provide the url to the ledger where 
            you want to publish the did setting the --public-did-ledger property"""
    )

    parse.add_argument(
        "--public-did-ledger",
        type=str,
        metavar=("<public-did-ledger>"),
        help="Ledger to publish public did"
    )

    parse.add_argument(
        "--webhook-url",
        type=str,
        metavar=("<webhook-url#api_key>"),
        help="""Send webhooks containing internal state changes to the   
                specified URL. Optional API key to be passed in the      
                request body can be appended using a hash separator      
                [#]. This is useful for a controller to monitor agent    
                events and respond to those events using the admin       
                API. If not specified, webhooks are not published by     
                the agent. [env var: ACAPY_WEBHOOK_URL]"""
    )

    parse.add_argument(
        "--auto-accept-invites",
        type=bool,
        const=False,
        nargs="?",
        metavar=("<auto-accept-invites>"),
        help='''Automatically accept invites without firing a webhook event or waiting for an admin request.
                Default: false. [env var: ACAPY_AUTO_ACCEPT_INVITES]'''
    )

    parse.add_argument(
        '--plugin', 
        action='append', 
        help='''
            Load <module> as external plugin module. Multiple instances of this parameter can be
            specified. [env var: ACAPY_PLUGIN]', required=True)
        '''
    )

    args = parse.parse_args()

    return args

if __name__ == "__main__":
    args = get_args()
    
    print(args)

    agent_args = {
        "identity": args.identity or os.getenv('identity'),
        "http_port": args.port or os.getenv('port'),
        "admin_port": args.admin_port or os.getenv('admin_port'),
        "public_did": args.public_did or os.getenv('public_did'),
        "public_did_ledger": args.public_did_ledger or os.getenv('public_did_ledger'),
        "genesis_url": args.genesis_url or os.getenv('genesis_url'),
        "seed": "random",
        "label": args.label or os.getenv('label'),
        "webhook_url": args.webhook_url or os.getenv('webhook_url'),
        "external_host": os.getenv('external_host') or 'localhost',
        "auto_accept_invites": args.auto_accept_invites or os.getenv('auto_accept_invites'),
        "plugins": (args.plugin or []) + (os.getenv('plugin') or [])
        
    }

    
    try:
        asyncio.get_event_loop().run_until_complete(main(agent_args))
    except KeyboardInterrupt:
        os._exit(1)

