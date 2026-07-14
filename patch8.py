import re

with open('temp.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update buyShopItem
old_buy = r"if\(\!confirm\(`Xác nhận mua vật phẩm này với giá \$\{price\} 🪙\?`\)\) return;\s*try \{(.*?)\} catch\(e\) \{\s*toast\(e\.message, 'error'\);\s*\}"

new_buy = r"""customConfirm(`Bạn có chắc muốn mua vật phẩm này với giá ${formatCoins(price)} Z-Coins?`, async () => {
    try {\1
      renderShop();
    } catch(e) {
      toast(e.message, 'error');
    }
  });"""

c = re.sub(old_buy, new_buy, c, flags=re.DOTALL)

# 2. Add inventory to user menu
old_menu = r"(<button class=\"dd-item\" onclick=\"navigate\('/profile/'\+currentUser\.id\);closeMenu\(\)\">\s*<svg.*?</svg>\s*Hồ sơ của tôi\s*</button>)"
new_menu = r"\1\n      <button class=\"dd-item\" onclick=\"navigate('/inventory');closeMenu()\">\n        <svg width=\"15\" height=\"15\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2\"/><path d=\"M4 10h16M10 16h4M4 4h16v6H4z\"/></svg>\n        Túi đồ 🎒\n      </button>"

c = re.sub(old_menu, new_menu, c)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch 8 applied.")
