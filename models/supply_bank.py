from threading import Lock
from config.shop_config import ShopItem

class SupplyBank:
    def __init__(self, shop_items_catalog: tuple[ShopItem, ...]):
        # Map the item to its current active stock for this specific game
        self._inventory: dict[ShopItem, int] = {
            item: item.starting_quantity for item in shop_items_catalog
        }
        # A threading lock to prevent race conditions
        self._lock = Lock()

    def __getitem__(self, item: ShopItem) -> int:
        """Read-only remaining stock lookup."""
        return self._inventory.get(item, 0)

    def purchase_item(self, item: ShopItem) -> bool:
        """Atomically check and decrement the supply of a chip."""
        with self._lock:
            if self._inventory.get(item, 0) > 0:
                self._inventory[item] -= 1
                return True
            return False
