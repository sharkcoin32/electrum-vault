from typing import List

from electrum.bitcoin import opcodes, push_script
from electrum.three_keys.multisig_generator import MultisigScriptGenerator


class ThreeKeysError(Exception):
    pass


class TwoKeysScriptGenerator(MultisigScriptGenerator):
    def __init__(self, recovery_pubkey: str):
        self.recovery_pubkey = recovery_pubkey
        self._recovery_alert_flag = None

    def get_redeem_script(self, public_keys: List[str]) -> str:
        if not isinstance(public_keys, list) or len(public_keys) != 1:
            raise ThreeKeysError(f"Wrong input type! Expected list not '{public_keys}'")

        pub_key = public_keys[0]
        return (
                opcodes.OP_IF.hex() +
                opcodes.OP_1.hex() +
                opcodes.OP_ELSE.hex() +
                opcodes.OP_2.hex() +
                opcodes.OP_ENDIF.hex() +

                push_script(pub_key) +
                push_script(self.recovery_pubkey) +

                opcodes.OP_2.hex() +
                opcodes.OP_CHECKMULTISIG.hex()
        )

    def get_script_sig(self, signatures: List[str], public_keys: List[str]) -> str:
        if self._recovery_alert_flag is None:
            raise ThreeKeysError('Recovery/alert flag not set!')
        sigs = ''.join(push_script(sig) for sig in signatures)
        return (
            opcodes.OP_0.hex() +
            sigs +
            self._recovery_alert_flag +
            push_script(self.get_redeem_script(public_keys))
        )

    def set_alert(self):
        # 1 of 2
        self._recovery_alert_flag = opcodes.OP_1.hex()

    def set_recovery(self):
        # 2 of 2
        self._recovery_alert_flag = opcodes.OP_0.hex()


class ThreeKeysScriptGenerator(MultisigScriptGenerator):
    def __init__(self, recovery_pubkey: str, instant_pubkey: str):
        self.recovery_pubkey = recovery_pubkey
        self.instant_pubkey = instant_pubkey
        self._instant_recovery_alert_flag = None

    def get_redeem_script(self, public_keys: List[str]) -> str:
        if not isinstance(public_keys, list) or len(public_keys) != 1:
            raise ThreeKeysError(f"Wrong input type! Expected list not '{public_keys}'")

        pub_key = public_keys[0]
        return (
                opcodes.OP_IF.hex() +
                opcodes.OP_1.hex() +
                opcodes.OP_ELSE.hex() +
                opcodes.OP_IF.hex() +
                opcodes.OP_2.hex() +
                opcodes.OP_ELSE.hex() +
                opcodes.OP_3.hex() +
                opcodes.OP_ENDIF.hex() +
                opcodes.OP_ENDIF.hex() +

                push_script(pub_key) +
                push_script(self.instant_pubkey) +
                push_script(self.recovery_pubkey) +

                opcodes.OP_3.hex() +
                opcodes.OP_CHECKMULTISIG.hex()
        )

    def get_script_sig(self, signatures: List[str], public_keys: List[str]) -> str:
        if self._instant_recovery_alert_flag is None:
            raise ThreeKeysError('Recovery/alert/instant flag not set!')
        sigs = ''.join(push_script(sig) for sig in signatures)
        return (
            opcodes.OP_0.hex() +
            sigs +
            self._instant_recovery_alert_flag +
            push_script(self.get_redeem_script(public_keys))
        )

    def set_alert(self):
        # 1 of 3
        self._instant_recovery_alert_flag = opcodes.OP_1.hex()

    def set_recovery(self):
        # 3 of 3
        self._instant_recovery_alert_flag = opcodes.OP_0.hex() + opcodes.OP_0.hex()

    def set_instant(self):
        # 2 of 3
        self._instant_recovery_alert_flag = opcodes.OP_1.hex() + opcodes.OP_0.hex()
