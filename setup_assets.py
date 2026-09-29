import os
import shutil

src_dir = r"C:\Users\cmsad\.gemini\antigravity-ide\brain\f76e8ff7-9e03-4349-917c-28331009e9f8"
dest_dir = r"d:\Cococare 2\frontend\assets\images"
os.makedirs(dest_dir, exist_ok=True)

image_mappings = {
    "hero_coconut_plantation_1786290636978.png": "hero_coconut_plantation.png",
    "coconut_leaf_detail_1786290653192.png": "coconut_leaf_detail.png",
    "healthy_coconut_tree_1786290669598.png": "healthy_coconut_tree.png",
    "coconut_grove_1786290690467.png": "coconut_grove.png"
}

for src_name, dest_name in image_mappings.items():
    src_path = os.path.join(src_dir, src_name)
    dest_path = os.path.join(dest_dir, dest_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)
        print(f"Copied {src_name} -> {dest_name}")

# Also copy assets to backend uploads so they can be served as static files if needed
uploads_dir = r"d:\Cococare 2\uploads"
for src_name, dest_name in image_mappings.items():
    src_path = os.path.join(src_dir, src_name)
    dest_path = os.path.join(uploads_dir, dest_name)
    if os.path.exists(src_path):
        shutil.copy(src_path, dest_path)

print("Image assets setup complete.")
