from time import sleep

from PyQt6.QtCore import QThread, pyqtSignal

from .otsconfig import config
from .runtimedata import account_pool, get_logger

logger = get_logger("accounts")


class FillAccountPool(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(str, bool)

    def __init__(self, gui=False):
        self.gui = gui
        super().__init__()


    def run(self):
        accounts = config.get('accounts')
        for account in accounts:
            service = account['service']
            if not account['active']:
                continue

            if self.gui:
                self.progress.emit(self.tr('Attempting to create session for\n{0}...').format(account['uuid']), True)

            valid_login = globals()[f"{service}_login_user"](account)
            if valid_login:
                if self.gui:
                    self.progress.emit(self.tr('Session created for\n{0}!').format(account['uuid']), True)
                continue
            else:
                if self.gui:
                    self.progress.emit(self.tr('Login failed for \n{0}!').format(account['uuid']), True)
                    sleep(0.5)
                continue

        self.finished.emit()


def get_account_token(item_service, rotate=False):
    if item_service in ('bandcamp', 'youtube_music', 'generic'):
        return
    parsing_index = config.get('active_account_number')
    if item_service == account_pool[parsing_index]['service'] and not rotate:
        return globals()[f"{item_service}_get_token"](parsing_index)
    else:
        for i in range(parsing_index + 1, parsing_index + len(account_pool) + 1):
            index = i % len(account_pool)
            if item_service == account_pool[index]['service']:
                if config.get("rotate_active_account_number"):
                    logger.debug(f"Returning {account_pool[index]['service']} account number {index}: {account_pool[index]['uuid']}")
                    config.set('active_account_number', index)
                    config.save()
                return globals()[f"{item_service}_get_token"](index)
