if (process.argv.length < 3) {
    console.log("Not enough parameters where given");
    exit(0)
}

let [js, file, ...inputs] = process.argv

for (const input of inputs) {
    console.log(input);
}