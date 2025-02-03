function isDeelbaar(x) {
    return x % 43 == 0;
}

let x = 13729;
console.log(x + " is deelbaar door 43: " + isDeelbaar(x));

x = 14706;
let deelbaar = isDeelbaar(x);
console.log(x + " is deelbaar door 43: " + deelbaar);