const testUtils = require('./testUtils.js');
const SOURCE_DIR = process.env['SOURCE_DIR'];

function findMatchingClosingBrace(content, startIndex) {
    let counter = 1;  // Start with 1 to account for the opening brace at startIndex

    for (let i = startIndex + 1; i < content.length; i++) {
        if (content[i] === '{') {
            counter++;
        } else if (content[i] === '}') {
            counter--;

            if (counter === 0) {
                return i;  // Found the matching closing brace
            }
        }
    }

    return -1;  // Matching closing brace not found
}

describe("TestSuite", function () {

    /**
    * Test of de juiste devdependencies gevonden kunnen worden voor ESLint.
    */
    it("Zijn de juiste libraries geïmporteerd voor jou als programmeur", function () {
        const expectedWords = ["eslint", "eslint-config-airbnb-base", "eslint-plugin-import"];
        const content = testUtils.readScriptSync('package.json');

        const devDependenciesStartIndex = content.indexOf('"devDependencies"');

        if (devDependenciesStartIndex === -1) {
            fail('"devDependencies" niet gevonden in package.json. Zorg ervoor dat de code alleen draait voor jou als developer en niet ook in productie.');
            return; // not strictly necessary
        }

        const devDependenciesOpenBraceIndex = content.indexOf('{', devDependenciesStartIndex);
        if (devDependenciesOpenBraceIndex === -1) {
            fail('"devDependencies" wordt niet goed geopend. Heb je de accolades op de juiste plek geopend en gesloten?');
            return;
        }

        const devDependenciesCloseBraceIndex = findMatchingClosingBrace(content, devDependenciesOpenBraceIndex);
        if (devDependenciesCloseBraceIndex === -1) {
            fail('"devDependencies" wordt niet goed afgesloten. Heb je de accolades op de juiste plek geopend en gesloten?');
            return;
        }

        const devDependenciesContent = content.slice(devDependenciesOpenBraceIndex + 1, devDependenciesCloseBraceIndex);

        // Controleer of de verwachte keywords aanwezig zijn in de content van 'devDependencies'
        expectedWords.forEach(keyword => {
            expect(devDependenciesContent).toContain(keyword);
        });
    });

});
