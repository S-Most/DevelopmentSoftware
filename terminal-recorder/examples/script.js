let data = ["Hello", 3, 3.2, "3", true, false, 3.0 + 3, 3 + "3"];

for (const waarde of data) {
    let type = typeof waarde;

    if (type == "number") {
        type += Number.isInteger(waarde) ? " int" : " float";
    }

    console.log(`Waarde ${waarde} heeft als type ${type}.`);
}