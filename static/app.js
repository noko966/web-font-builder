document.addEventListener("DOMContentLoaded", () => {
  const fontContainer = document.getElementById("font-container");

  // Function to dynamically add @font-face rule to the document
  function addFontFace(fontName, fontUrl) {
    const style = document.createElement("style");
    style.innerHTML = `
      @font-face {
        font-family: '${fontName}';
        src: url('${fontUrl}.eot'); /* IE9 Compat Modes */
        src: url('${fontUrl}.eot?#iefix') format('embedded-opentype'), /* IE6-IE8 */
             url('${fontUrl}.woff2') format('woff2'), /* Super Modern Browsers */
             url('${fontUrl}.woff') format('woff'), /* Modern Browsers */
             url('${fontUrl}.ttf') format('truetype'); /* Safari, Android, iOS */
        font-weight: normal;
        font-style: normal;
      }
    `;
    document.head.appendChild(style);
  }

// Function to load and render the font and its mapping from the server
async function loadFont() {
  try {
    const response = await fetch("/fonts");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const fontFiles = await response.json();
    if (fontFiles.length === 0) {
      console.warn("No fonts found.");
      return;
    }

    // Assuming the first font file as base name without extension
    const fontName = "CustomFont";
    const baseUrl = `/static/fonts/${fontFiles[0].split(".")[0]}`;

    addFontFace(fontName, baseUrl);

    // Fetch the font mapping
    const mappingResponse = await fetch(`/get_font_data?name=${fontName}`);
    if (!mappingResponse.ok) {
      throw new Error("Network response for mapping was not ok");
    }
    const fontData = await mappingResponse.json();
    const glyphs = fontData.glyphs;

    // Clear existing glyphs
    fontContainer.innerHTML = "";

    // Render each glyph according to the mapping
    glyphs.forEach(glyph => {

      const codePoint = document.createElement("span");
      codePoint.className = "code_point";
      codePoint.innerText = glyph.codepoint;

      const glyphElement = document.createElement("div");
      glyphElement.className = "glyph";
      

      const glyphElementIcon = document.createElement("i");
      glyphElementIcon.className = "glyph_icon";
      glyphElementIcon.innerText = String.fromCharCode(parseInt(glyph.codepoint, 16));
      glyphElement.style.fontFamily = fontName;

      const glyphInputWrapper = document.createElement("div");
      glyphInputWrapper.className = "glyph_input_wrapper";

      const glyphInput = document.createElement("input");
      glyphInput.type = "text";
      glyphInput.value = glyph.glyph_name;
      glyphInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          updateGlyphName(fontName, glyph.glyph_name, glyphInput.value);
        }
      });

      const editIcon = document.createElement("span");
      editIcon.className = "edit_icon";
      editIcon.innerHTML = "&#9998;"; // Unicode for edit icon
      editIcon.addEventListener("click", () => {
        glyphInput.focus();
      });
      
      fontContainer.appendChild(glyphElement);
      glyphInputWrapper.appendChild(glyphInput);
      glyphInputWrapper.appendChild(editIcon);

      glyphElement.appendChild(codePoint);
      glyphElement.appendChild(glyphElementIcon);
      glyphElement.appendChild(glyphInputWrapper);
    });
  } catch (error) {
    console.error("Error loading font:", error);
  }
}


  // Function to update the glyph name
  async function updateGlyphName(fontName, oldGlyphName, newGlyphName) {
    try {
      const response = await fetch('/update_glyph_name', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          font_name: fontName,
          old_glyph_name: oldGlyphName,
          new_glyph_name: newGlyphName
        })
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      console.log(result.message);

      // Reload the font to reflect the changes
      loadFont();
    } catch (error) {
      console.error("Error updating glyph name:", error);
    }
  }

  // Initial load
  loadFont();
});
