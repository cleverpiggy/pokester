HOST = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpQRkxmZTVCY1lBS25YalBaeWkwdCJ9.eyJpc3MiOiJodHRwczovL2NsZXZlcnBpZ2d5LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjA1ZWY0MjNlMGRlODAwMTM5ZGY4ZDUiLCJhdWQiOlsiaHR0cHM6Ly9wb2tlc3Rlci5oZXJva3VhcHAuY29tIiwiaHR0cHM6Ly9jbGV2ZXJwaWdneS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTk0NTkyNTQ1LCJleHAiOjE1OTQ2Nzg5NDUsImF6cCI6IlJtYUZHZ1NENjVjR2ZmTWZZcEZUQmh5S3I2a3VtS25pIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiY3JlYXRlOmdhbWUiLCJkZWxldGU6Z2FtZSIsImVkaXQ6Z2FtZSIsImpvaW46Z2FtZSJdfQ.hpnIhqlb5g25Ccgk28lWE5fxN6GsKNziM5tt3najgXXbjqL5FV2q62Ma4OU_YS-lGzmUYkhquIpjEZ7i9_0LuXoD1CCb9wWiZCzaF_hathxcopjNDFLCu6SkHj8MoDOTYHO8aqw9HTsAeiY-88IM1UkgfM0rysOeNwZJcihQJ94hS-xKfyx8Hl1LNr6z5uU0lBaPTphzjWCIUVpvVYbQYKjV7eJp1sDH3UAYhUVSq2lmsDqvgA5tfqxAPP3cteRmNJZ2Fjek3uhjJLf5IDqpw6gSy_IufwpbgmJ0sEAb43VxiSkT2K4xeeBWioH4MAfiQTAkaKZJas9g4SsbXmqTcg'
PLAYER = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpQRkxmZTVCY1lBS25YalBaeWkwdCJ9.eyJpc3MiOiJodHRwczovL2NsZXZlcnBpZ2d5LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjAzOGI2OTkyODgyYzAwMTM1ZjM3MTQiLCJhdWQiOlsiaHR0cHM6Ly9wb2tlc3Rlci5oZXJva3VhcHAuY29tIiwiaHR0cHM6Ly9jbGV2ZXJwaWdneS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTk0NTkyNDY5LCJleHAiOjE1OTQ2Nzg4NjksImF6cCI6IlJtYUZHZ1NENjVjR2ZmTWZZcEZUQmh5S3I2a3VtS25pIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImd0eSI6InBhc3N3b3JkIiwicGVybWlzc2lvbnMiOlsiam9pbjpnYW1lIl19.UquBP4uGJuEJrPEb90-Yq6rtqhKkr8w40oLcBgNd3yK9Tt1qkE0EeKFFB1Qu3-HxeLRlZI5K8T0Jc0nxGmfZ7VvPDGZDbr_SbeRn1fZkCWQsifc1Njpc54nV2K10UxjYqculjvJZ4aS3Klc61tHpDsoRrDtQ2Z1K2LCvxsBR6te8CllejPmgLh7UTlVa2j_01PJd5DD5pTMy7WX533zVNRMUhsT-SaNA-w_IWPxXzoPtnY7jjdH4YNbFcvrZK19cDUjXYC3BP63w9SuwXZasCedHGLjOV_34EIui7hon2susS-GKN2xghzmHhgSBjnIDLWPMjtmXEWx2TNo5mfh_Pg'
EXPIRED = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpQRkxmZTVCY1lBS25YalBaeWkwdCJ9.eyJpc3MiOiJodHRwczovL2NsZXZlcnBpZ2d5LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjA1ZWY0MjNlMGRlODAwMTM5ZGY4ZDUiLCJhdWQiOlsiaHR0cHM6Ly9wb2tlc3Rlci5oZXJva3VhcHAuY29tIiwiaHR0cHM6Ly9jbGV2ZXJwaWdneS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTk0NTc3ODE0LCJleHAiOjE1OTQ1Nzc4MTUsImF6cCI6IlJtYUZHZ1NENjVjR2ZmTWZZcEZUQmh5S3I2a3VtS25pIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbImNyZWF0ZTpnYW1lIiwiZGVsZXRlOmdhbWUiLCJlZGl0OmdhbWUiLCJqb2luOmdhbWUiXX0.GDlk2otRueTyor3drobnzj7Ivh9OXcvTtYLBrcR2pDIE4XdrN1VQXNhHnM-U_gX81Jm1M4-1YLyaR9Boo-acvaSTzSG_Q35CRlwDN1w3Kf2CjfM-xHvr5CpdfmhE3vPJTO2GHeJagLcJW9ExKoDEuwoznH365JMfC-B60fIOJwxuYN9gqLE7ZcUjBSUE_kZBTmY1pHOaMVfiO9qYbn12sTNEIBYhuCz-OkLh7UrI7aqeUPNyaaSnPn39_AG-GY-pzB7ImbAoLMqMDdhy4x99Mzj4VjCXjZLrXfd6LhaWCuxmCMxtyZacDpiYvjXRsCIfzqvf26wZH8Fjn4zQvBF0Bg'