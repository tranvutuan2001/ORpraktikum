\ Model Heatpumps
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  P(H1,B1) + 2 P(H2,B1) + 3 P(H3,B1) + 4 P(H4,B1) + 5 P(H5,B1) + P(H1,B2)
   + 2 P(H2,B2) + 3 P(H3,B2) + 4 P(H4,B2) + 5 P(H5,B2) + P(H1,B3)
   + 2 P(H2,B3) + 3 P(H3,B3) + 4 P(H4,B3) + 5 P(H5,B3) + P(H1,B4)
   + 2 P(H2,B4) + 3 P(H3,B4) + 4 P(H4,B4) + 5 P(H5,B4) + P(H1,B5)
   + 2 P(H2,B5) + 3 P(H3,B5) + 4 P(H4,B5) + 5 P(H5,B5) + P(H1,B6)
   + 2 P(H2,B6) + 3 P(H3,B6) + 4 P(H4,B6) + 5 P(H5,B6) + P(H1,B7)
   + 2 P(H2,B7) + 3 P(H3,B7) + 4 P(H4,B7) + 5 P(H5,B7) + P(H1,B8)
   + 2 P(H2,B8) + 3 P(H3,B8) + 4 P(H4,B8) + 5 P(H5,B8) + P(H1,B9)
   + 2 P(H2,B9) + 3 P(H3,B9) + 4 P(H4,B9) + 5 P(H5,B9) + P(H1,B10)
   + 2 P(H2,B10) + 3 P(H3,B10) + 4 P(H4,B10) + 5 P(H5,B10)
Subject To
 R0: P(H1,B1) + P(H2,B1) + P(H3,B1) + P(H4,B1) + P(H5,B1) <= 1
 R1: P(H1,B2) + P(H2,B2) + P(H3,B2) + P(H4,B2) + P(H5,B2) <= 1
 R2: P(H1,B3) + P(H2,B3) + P(H3,B3) + P(H4,B3) + P(H5,B3) <= 1
 R3: P(H1,B4) + P(H2,B4) + P(H3,B4) + P(H4,B4) + P(H5,B4) <= 1
 R4: P(H1,B5) + P(H2,B5) + P(H3,B5) + P(H4,B5) + P(H5,B5) <= 1
 R5: P(H1,B6) + P(H2,B6) + P(H3,B6) + P(H4,B6) + P(H5,B6) <= 1
 R6: P(H1,B7) + P(H2,B7) + P(H3,B7) + P(H4,B7) + P(H5,B7) <= 1
 R7: P(H1,B8) + P(H2,B8) + P(H3,B8) + P(H4,B8) + P(H5,B8) <= 1
 R8: P(H1,B9) + P(H2,B9) + P(H3,B9) + P(H4,B9) + P(H5,B9) <= 1
 R9: P(H1,B10) + P(H2,B10) + P(H3,B10) + P(H4,B10) + P(H5,B10) <= 1
 R10: 100 P(H1,B2) + 100 P(H2,B2) + 100 P(H3,B2) + 100 P(H4,B2)
   + 100 P(H5,B2) + 200 P(H1,B3) + 200 P(H2,B3) + 200 P(H3,B3)
   + 200 P(H4,B3) + 200 P(H5,B3) + 300 P(H1,B4) + 300 P(H2,B4)
   + 300 P(H3,B4) + 300 P(H4,B4) + 300 P(H5,B4) + 400 P(H1,B5)
   + 400 P(H2,B5) + 400 P(H3,B5) + 400 P(H4,B5) + 400 P(H5,B5)
   + 500 P(H1,B6) + 500 P(H2,B6) + 500 P(H3,B6) + 500 P(H4,B6)
   + 500 P(H5,B6) + 600 P(H1,B7) + 600 P(H2,B7) + 600 P(H3,B7)
   + 600 P(H4,B7) + 600 P(H5,B7) + 700 P(H1,B8) + 700 P(H2,B8)
   + 700 P(H3,B8) + 700 P(H4,B8) + 700 P(H5,B8) + 800 P(H1,B9)
   + 800 P(H2,B9) + 800 P(H3,B9) + 800 P(H4,B9) + 800 P(H5,B9)
   + 900 P(H1,B10) + 900 P(H2,B10) + 900 P(H3,B10) + 900 P(H4,B10)
   + 900 P(H5,B10) >= 2000
Bounds
Binaries
 P(H1,B1) P(H2,B1) P(H3,B1) P(H4,B1) P(H5,B1) P(H1,B2) P(H2,B2) P(H3,B2)
 P(H4,B2) P(H5,B2) P(H1,B3) P(H2,B3) P(H3,B3) P(H4,B3) P(H5,B3) P(H1,B4)
 P(H2,B4) P(H3,B4) P(H4,B4) P(H5,B4) P(H1,B5) P(H2,B5) P(H3,B5) P(H4,B5)
 P(H5,B5) P(H1,B6) P(H2,B6) P(H3,B6) P(H4,B6) P(H5,B6) P(H1,B7) P(H2,B7)
 P(H3,B7) P(H4,B7) P(H5,B7) P(H1,B8) P(H2,B8) P(H3,B8) P(H4,B8) P(H5,B8)
 P(H1,B9) P(H2,B9) P(H3,B9) P(H4,B9) P(H5,B9) P(H1,B10) P(H2,B10) P(H3,B10)
 P(H4,B10) P(H5,B10)
End
