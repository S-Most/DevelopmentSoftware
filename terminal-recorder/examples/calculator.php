<?php

$operator = readline("Welke operatie wil je uitvoeren? (+, -, %)" . PHP_EOL);

// Gelijk checken of de operator klopt, anders het script stoppen met exit()
if ($operator !== "+" && $operator !== "-" && $operator !== "%") {
    exit("'$operator' is geen geldige operatie" . PHP_EOL);
}

// Getal opvragen en checken of het een numerieke waarde heeft. Anders exit()
$number1 = readline("Eerste getal?" . PHP_EOL);
if (!is_numeric($number1)) {
    exit("'$number1' is geen getal" . PHP_EOL);
}

// Getal opvragen en checken of het een numerieke waarde heeft. Anders exit()
$number2 = readline("Tweede getal?" . PHP_EOL);
if (!is_numeric($number2)) {
    exit("'$number2' is geen getal". PHP_EOL);
}

// Resultaat laten zien gebaseerd op welke operator er is gekozen
if ($operator === "+") {
    echo $number1 + $number2 . PHP_EOL;
} elseif ($operator === "-") {
    echo $number1 - $number2 . PHP_EOL;
} elseif($operator === "%") {
    echo $number1 % $number2 . PHP_EOL;
}