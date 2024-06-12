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

  // Function to load and render the font from the server
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

      // Clear existing glyphs
      fontContainer.innerHTML = "";

      // Render each glyph in the range E000 - E030
      for (let codePoint = 0xe000; codePoint <= 0xe030; codePoint++) {
        const glyphElement = document.createElement("div");
        glyphElement.className = "glyph";
        glyphElement.innerText = String.fromCharCode(codePoint);
        glyphElement.style.fontFamily = fontName;
        fontContainer.appendChild(glyphElement);
      }
    } catch (error) {
      console.error("Error loading font:", error);
    }
  }

  // Polling function to check for font file changes
  function pollFontChanges() {
    setInterval(() => {
      loadFont();
    }, 10000); // Check every 10 seconds (adjust as needed)
  }

  // Initial load
  loadFont();
  pollFontChanges();
});
