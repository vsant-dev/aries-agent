import pytest

from asynctest import mock as async_mock

from aries_askar import AskarError, AskarErrorCode

from ...askar.profile import AskarProfileManager
from ...config.injection_context import InjectionContext
from ...core.in_memory import InMemoryProfile
from ...ledger.endpoint_type import EndpointType

from ..base import BaseWallet
from ..did_method import DIDMethod
from ..in_memory import InMemoryWallet
from ..key_type import KeyType
from .. import askar as test_module

from . import test_in_memory_wallet


@pytest.fixture()
async def in_memory_wallet():
    profile = InMemoryProfile.test_profile()
    wallet = InMemoryWallet(profile)
    yield wallet


@pytest.fixture()
async def wallet():
    context = InjectionContext()
    profile = await AskarProfileManager().provision(
        context,
        {
            # "auto_recreate": True,
            # "auto_remove": True,
            "name": ":memory:",
            "key": await AskarProfileManager.generate_store_key(),
            "key_derivation_method": "RAW",  # much faster than using argon-hashed keys
        },
    )
    async with profile.session() as session:
        yield session.inject(BaseWallet)
    del session
    # this will block indefinitely if session or profile references remain
    # await profile.close()


@pytest.mark.askar
class TestAskarWallet(test_in_memory_wallet.TestInMemoryWallet):
    """Apply all InMemoryWallet tests against AskarWallet"""

    # overriding derived values - Askar follows bls signatures draft 4 in key generation
    test_key_bls12381g2_did = "did:key:zUC74E9UD2W6Q1MgPexCEdpstiCsY1Vbnyqepygk7McZVce38L1tGX7qZ2SgY4Zz2m9FUB4Xb5cEHSujks9XeKDzqe4QzW3CyyJ1cv8iBLNqU61EfkBoW2yEkg6VgqHTDtANYRS"
    test_bls12381g2_verkey = "pPbb9Lqs3PVTyiHM4h8fbQqxHjBPm1Hixb6vdW9kkjHEij4FZrigkaV1P5DjWTbcKxeeYfkQuZMmozRQV3tH1gXhCA972LAXMGSKH7jxz8sNJqrCR6o8asgXDeYZeL1W3p8"

    @pytest.mark.skip
    @pytest.mark.asyncio
    async def test_rotate_did_keypair_x(self, wallet):
        info = await wallet.create_local_did(
            DIDMethod.SOV, KeyType.ED25519, self.test_seed, self.test_did
        )

        with async_mock.patch.object(
            indy.did, "replace_keys_start", async_mock.CoroutineMock()
        ) as mock_repl_start:
            mock_repl_start.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.rotate_did_keypair_start(self.test_did)
            assert "outlier" in str(excinfo.value)

        with async_mock.patch.object(
            indy.did, "replace_keys_apply", async_mock.CoroutineMock()
        ) as mock_repl_apply:
            mock_repl_apply.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.rotate_did_keypair_apply(self.test_did)
            assert "outlier" in str(excinfo.value)

    @pytest.mark.skip
    @pytest.mark.asyncio
    async def test_create_signing_key_x(self, wallet):
        with async_mock.patch.object(
            indy.crypto, "create_key", async_mock.CoroutineMock()
        ) as mock_create_key:
            mock_create_key.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.create_signing_key()
            assert "outlier" in str(excinfo.value)

    @pytest.mark.skip
    @pytest.mark.asyncio
    async def test_create_local_did_x(self, wallet):
        with async_mock.patch.object(
            indy.did, "create_and_store_my_did", async_mock.CoroutineMock()
        ) as mock_create:
            mock_create.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.create_local_did(
                    DIDMethod.SOV,
                    KeyType.ED25519,
                )
            assert "outlier" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_set_did_endpoint_ledger(self, wallet):
        mock_ledger = async_mock.MagicMock(
            read_only=False, update_endpoint_for_did=async_mock.CoroutineMock()
        )
        info_pub = await wallet.create_public_did(
            DIDMethod.SOV,
            KeyType.ED25519,
        )
        await wallet.set_did_endpoint(info_pub.did, "http://1.2.3.4:8021", mock_ledger)
        mock_ledger.update_endpoint_for_did.assert_called_once_with(
            info_pub.did, "http://1.2.3.4:8021", EndpointType.ENDPOINT
        )
        info_pub2 = await wallet.get_public_did()
        assert info_pub2.metadata["endpoint"] == "http://1.2.3.4:8021"

        with pytest.raises(test_module.LedgerConfigError) as excinfo:
            await wallet.set_did_endpoint(info_pub.did, "http://1.2.3.4:8021", None)
        assert "No ledger available" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_set_did_endpoint_readonly_ledger(self, wallet):
        mock_ledger = async_mock.MagicMock(
            read_only=True, update_endpoint_for_did=async_mock.CoroutineMock()
        )
        info_pub = await wallet.create_public_did(
            DIDMethod.SOV,
            KeyType.ED25519,
        )
        await wallet.set_did_endpoint(info_pub.did, "http://1.2.3.4:8021", mock_ledger)
        mock_ledger.update_endpoint_for_did.assert_not_called()
        info_pub2 = await wallet.get_public_did()
        assert info_pub2.metadata["endpoint"] == "http://1.2.3.4:8021"

        with pytest.raises(test_module.LedgerConfigError) as excinfo:
            await wallet.set_did_endpoint(info_pub.did, "http://1.2.3.4:8021", None)
        assert "No ledger available" in str(excinfo.value)

    @pytest.mark.skip
    @pytest.mark.asyncio
    async def test_get_signing_key_x(self, wallet):
        with async_mock.patch.object(
            indy.crypto, "get_key_metadata", async_mock.CoroutineMock()
        ) as mock_signing:
            mock_signing.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.get_signing_key(None)
            assert "outlier" in str(excinfo.value)

    @pytest.mark.skip
    @pytest.mark.asyncio
    async def test_get_local_did_x(self, wallet):
        with async_mock.patch.object(
            indy.did, "get_my_did_with_meta", async_mock.CoroutineMock()
        ) as mock_my:
            mock_my.side_effect = test_module.IndyError(
                test_module.ErrorCode.CommonIOError, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.get_local_did(None)
            assert "outlier" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_verify_message_x(self, wallet):
        with async_mock.patch.object(
            test_module.Key, "verify_signature"
        ) as mock_verify:
            mock_verify.side_effect = test_module.AskarError(  # outlier
                AskarErrorCode.BACKEND, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.verify_message(
                    b"hello world",
                    b"signature",
                    self.test_ed25519_verkey,
                    KeyType.ED25519,
                )

    @pytest.mark.asyncio
    async def test_pack_message_x(self, wallet):
        with async_mock.patch.object(
            test_module,
            "_pack_message",
        ) as mock_pack:
            mock_pack.side_effect = AskarError(  # outlier
                AskarErrorCode.BACKEND, {"message": "outlier"}
            )
            with pytest.raises(test_module.WalletError) as excinfo:
                await wallet.pack_message(
                    b"hello world",
                    [
                        self.test_ed25519_verkey,
                    ],
                )


@pytest.mark.askar
class TestWalletCompat:
    """Tests for wallet compatibility."""

    test_seed = "testseed000000000000000000000001"
    test_did = "55GkHamhTU1ZbTbV2ab9DE"
    test_verkey = "3Dn1SJNPaCXcvvJvSbsFWP2xaCjMom3can8CQNhWrTRx"
    test_message = "test message"

    @pytest.mark.asyncio
    async def test_compare_pack_unpack(self, in_memory_wallet, wallet):
        """
        Ensure that python-based pack/unpack is compatible with indy-sdk implementation
        """
        await in_memory_wallet.create_local_did(
            DIDMethod.SOV, KeyType.ED25519, self.test_seed
        )
        py_packed = await in_memory_wallet.pack_message(
            self.test_message, [self.test_verkey], self.test_verkey
        )

        await wallet.create_local_did(DIDMethod.SOV, KeyType.ED25519, self.test_seed)
        packed = await wallet.pack_message(
            self.test_message, [self.test_verkey], self.test_verkey
        )

        py_unpacked, from_vk, to_vk = await in_memory_wallet.unpack_message(packed)
        assert self.test_message == py_unpacked

        unpacked, from_vk, to_vk = await wallet.unpack_message(py_packed)
        assert self.test_message == unpacked
