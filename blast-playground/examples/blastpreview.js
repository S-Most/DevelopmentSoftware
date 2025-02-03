const testUtils = require('./testUtils.js');

describe("VariableDeclarationTestSuite", function () {

    /**
    * Test of de woorden 'let' en 'const' correct worden gebruikt in het JavaScript-bestand.
    */
    it("Gebruikt het bestand 'let' en 'const' woorden op de juiste manier", function () {
        // Vervang 'yourJavaScriptFile.js' met de werkelijke naam van je JavaScript-bestand.
        const content = testUtils.readScriptSync('yourJavaScriptFile.js');

        const letOccurrences = countOccurrences(content, 'let');
        const constOccurrences = countOccurrences(content, 'const');

        // Controleer of 'let' minimaal één keer wordt gebruikt (vaker dan 0)
        it("Gebruikt het woord 'let'", function () {
            expect(letOccurrences).toBeGreaterThan(0);
        });

        // Controleer of 'const' minimaal één keer wordt gebruikt (vaker dan 0)
        it("Gebruikt het woord 'const'", function () {
            expect(constOccurrences).toBeGreaterThan(0);
        });

        // Controleer of er geen 'let' en 'const' op dezelfde regel worden gebruikt
        it("Gebruikt niet 'let' en 'const' op dezelfde regel", function () {
            const lines = content.split('\n');
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes('let') && lines[i].includes('const')) {
                    fail(`Gebruikt 'let' en 'const' op dezelfde regel (regel ${i + 1})`);
                }
            }
        });
    });

    function countOccurrences(content, word) {
        const regex = new RegExp(`\\b${word}\\b`, 'g');
        const matches = content.match(regex);
        return matches ? matches.length : 0;
    }
});
