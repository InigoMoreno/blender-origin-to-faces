# Origin to Selected Faces (Align to XY) for Blender

**Author:** Iñigo Moreno i Caireta
**Version:** 1.0
**Blender Compatibility:** 3.0 and later
**Category:** Object

This Blender add-on allows you to set an object's origin to the median of a selection of faces and rotate the object so those faces lie flat on the global XY plane, **without moving the visible geometry**.

---

## Installation

1. **Download the add-on ZIP**
directly from GitHub: <https://github.com/InigoMoreno/blender-origin-to-faces/archive/refs/heads/main.zip>


2. **Install in Blender**

   * In Blender, go to **Edit → Preferences → Add-ons → Install…**
   * Select the downloaded ZIP file (do not extract).
   * Enable **Origin to Selected Faces (Align to XY)** in the add-on list.

---

## Usage

1. Select a mesh object and enter **Edit Mode**.
2. Select the coplanar faces you want to use as the reference.
3. Go to **Object → Set Origin → Origin to Selected Faces (Align to XY)**.

The add-on will:

* Set the object’s **origin** to the median of the selected faces.
* Rotate the object so the faces lie on the **global XY plane**.
* Keep the visible geometry in place (no movement of vertices).
