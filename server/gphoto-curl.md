# Get album info
curl "https://photoslibrary.googleapis.com/v1/albums" \
    -H "Authorization: Bearer ya29.a0ARrdaM8G3biixstQI2yRFyJpt34jM1hLB8oErjD1Rqe1-pSssgE2duWMc0fQ50fqIf77Oyxty7mn7-ZdJDI44nVjPYmm3M6ElJb90j5nKxEEyw4OsWAWAuplINtXYHZqoUcDmU-7nl3o40Da_PxOOM2NL9Oh"

# Upload phase 1
curl "https://photoslibrary.googleapis.com/v1/uploads" \
    -X POST \
    -H "Content-type: application/octet-stream" \
    -H "X-Goog-Upload-Protocol: raw" \
    -H "Authorization: Bearer ya29.a0ARrdaM8G3biixstQI2yRFyJpt34jM1hLB8oErjD1Rqe1-pSssgE2duWMc0fQ50fqIf77Oyxty7mn7-ZdJDI44nVjPYmm3M6ElJb90j5nKxEEyw4OsWAWAuplINtXYHZqoUcDmU-7nl3o40Da_PxOOM2NL9Oh" \
    -H "X-Goog-Upload-Content-Type: image/jpeg" \
    --data-binary @test.jpg 

# Upload phase 2
curl "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate" \
    -X POST \
    -H "Content-type: application/json" \
    -H "Authorization: Bearer ya29.a0ARrdaM8G3biixstQI2yRFyJpt34jM1hLB8oErjD1Rqe1-pSssgE2duWMc0fQ50fqIf77Oyxty7mn7-ZdJDI44nVjPYmm3M6ElJb90j5nKxEEyw4OsWAWAuplINtXYHZqoUcDmU-7nl3o40Da_PxOOM2NL9Oh" \
    -d '{"albumId": "AI3d0xwnNxU3to2s2CNO6wgKK9vzMqGLNt_O06U4aZCZZ6iez1_Dc2Gp8lN3keenC99PYBPfXs21", "newMediaItems": [{"description": "item-description-test", "simpleMediaItem": {"fileName": "myfile", "uploadToken": "CAIS+QIAqD4uLbmKkcpKJ+RM0udsoCKt1OeMNMM+31nETu1s1djGv/daR2GZzie8xjXkSrDtLYGvIQ1NJPZT2NnqLEk9UqpkeFWIx9kkKimhdPLiFbxiKfbToCZ6hoPpkU3jJPjKPxLMRXoxV4AvEmE5oQVNXsK8x5Y67X6J7lMkqfp9ODlY6Vmvg1QiOt1xYLhcCoa9F//h9lq1Ksdzhwvum40BbvMSsyAUW3FIIDZ6+Xk7c2SJwoPTKNK9mHVWzTJ6wid3Q2JfBHMjMCcascbstqlwjsPZ1W+oG+ZwpEb0VRTiZdyTKRmqwGTpvnxqQqaUuAJjF2pe9HJO+h7X3djXtRkgb2boNSddB+rsIDVLmrqBo8KLAm71SQbb3aqY5MvrGb5hkXTEGSGurSt0PjYdAPUnjSqehNI1l1MGbzxK+FyL4xPW+WNl37DLvGqirc+JeV4Oe6v9LVRW38rDsOSgUpns9OAJEmgFFsq7NpU7XKNL1lODwC+RKEF/DQ"}}]}'