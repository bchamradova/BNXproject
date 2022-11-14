
Data na serveru - Jeden scan obsahuje 4 banky
Každý bank má 137 sloupců a každému banku náleží 2 po sobě jdoucí runID, první runID obsahuje sloupce 1-69 druhé 70-137
Každému scanu tak přísluší 8 po sobě jdoucích runID
Příklad BNX:

runID 1, column 55 => scan 1 bank1, obrazek Scan01/Bank1/B1_CH1_C055
runID 8, column 132 => scan 1 bank 4 obrazek Scan01/Bank4/B4_CH1_C132
runID 10 => scan 2 bank 1
runID 11 => scan 2 bank 2
Na obrázku je chip saphyr, má tři flowcelly, každá flowcella má 4 banky (jeden bank = červený obdelník).
![](../../files/saphyrFlowcells.png)


run  scan   bank

1   1   1
2   1   1
3   1   2
4   1   2
5   1   3
6   1   3
7   1   4
8   1   4
9   2   1
10  2   1
11  2   2
12  2   2
13  2   3
...



flowcell zatim vzdycky 1
min snr 3?