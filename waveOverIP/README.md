https://github.com/amurzeau/waveOverUDP
http://www.orangepi.org/Docs/WiringPi.html
https://github.com/OrangePiLibra/WiringPi/issues/2
https://www.raspberrypi.org/forums/viewtopic.php?t=104814

 +------+-----+----------+------+---+OrangePiH3+---+------+----------+-----+------+
 | GPIO | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | GPIO |
 +------+-----+----------+------+---+----++----+---+------+----------+-----+------+
 |      |     |     3.3v |      |   |  1 || 2  |   |      | 5v       |     |      |
 |   12 |   0 |    SDA.0 |  OUT | 0 |  3 || 4  |   |      | 5v       |     |      |
 |   11 |   1 |    SCL.0 |  OUT | 0 |  5 || 6  |   |      | 0v       |     |      |
 |    6 |   2 |      PA6 |  OUT | 0 |  7 || 8  | 0 | OUT  | TxD2     | 3   | 0    |
 |      |     |       0v |      |   |  9 || 10 | 0 | OUT  | RxD2     | 4   | 1    |
 |  352 |   5 |    S-TWI | ALT2 | 0 | 11 || 12 | 0 | OFF  | PD11     | 6   | 107  |
 |  353 |   7 |    S-SDA | ALT2 | 0 | 13 || 14 |   |      | 0v       |     |      |
 |    3 |   8 |     CTS2 |  OUT | 0 | 15 || 16 | 0 | OUT  | SDA.1    | 9   | 19   |
 |      |     |     3.3v |      |   | 17 || 18 | 0 | OUT  | SCL.1    | 10  | 18   |
 |   15 |  11 |   MOSI.1 |   IN | 1 | 19 || 20 |   |      | 0v       |     |      |
 |   16 |  12 |   MISO.1 |  OUT | 1 | 21 || 22 | 0 | OUT  | RTS2     | 13  | 2    |
 |   14 |  14 |   SCLK.1 |  OUT | 0 | 23 || 24 | 0 | OUT  | CS.1     | 15  | 13   |
 |      |     |       0v |      |   | 25 || 26 | 0 | OUT  | PD14     | 16  | 110  |
 +------+-----+----------+------+---+----++----+---+------+----------+-----+------+
 | GPIO | wPi |   Name   | Mode | V | Physical | V | Mode | Name     | wPi | GPIO |
 +------+-----+----------+------+---+OrangePiH3+---+------+----------+-----+------+


https://github.com/xpertsavenue/WiringOP-Zero
https://github.com/wdmomoxx/WiringOP-Zero

OrangePi_H3_ZEROPLUS2