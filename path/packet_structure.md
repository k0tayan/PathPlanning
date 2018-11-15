### packet structure

| index | num |  
| :------: | :------: |
| 0 |checksum &#x7C; 0x80
| 1 |  x[0] >> 7 |   
| 2 |  x[0] & 0x7f | 
| 3 |  x[1] >> 7  |
| 4 |  x[1] & 0x7f | 
| 5 |  x[2] >> 0x7f | 
| 6 |  x[2] & 0x7f | 
| 7 |  x[3] >> 0x7f | 
| 8 |  x[3] & 0x7f | 
| 9 |  x[4] >> 0x7f |
| 10 | x[4] & 0x7f | 
| 11 | x[5] >> 0x7f |
| 12 | x[5] & 0x7f |  
| 13 | x[6] >> 0x7f |
| 14 | x[6] & 0x7f |  
| 15 | x[7] >> 0x7f |
| 16 | x[7] & 0x7f |  
| 17 | y[0] >> 7 | 
| 18 | y[0] & 0x7f |  
| 19 | y[1] >> 7 |
| 20 | y[2] & 0x7f | 
| ... | |
| 32 | y[8] & 0x7f |
| 33 | flippoint1 0b00Fiiixx F=failed(true == failed) iii=index xx=dir |  
| 34 | flippoint2 0b00Fiiixx F=failed(true == failed) iii=index xx=dir |
| 35 | flippoint3 0b00Fiiixx F=failed(true == failed) iii=index xx=dir |
| 36 | flippoint4 0b00Fiiixx F=failed(true == failed) iii=index xx=dir |

#### about flippoint 
**0 <= index <= 7**  

| dir | xx |  
| :-----: | :-----: |  
| 'LEFT' | 00 |  
| RIGHT' | 01 |
| 'FRONT' | 11 |

 
  