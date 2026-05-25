export default async function handler(req, res) {
  const { code } = req.query

  if (!code) {
    res.status(400).send('Missing code parameter')
    return
  }

  try {
    const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        client_id: process.env.OAUTH_CLIENT_ID,
        client_secret: process.env.OAUTH_CLIENT_SECRET,
        code,
      }),
    })

    const data = await tokenRes.json()

    if (data.error) {
      res.status(400).send(`GitHub OAuth error: ${data.error_description || data.error}`)
      return
    }

    res.setHeader('Content-Type', 'text/html')
    res.send(`<!doctype html><html><body><script>
      (function() {
        function receiveMessage(e) {
          window.opener.postMessage(
            'authorization:github:success:{"token":"${data.access_token}","provider":"github"}',
            e.origin
          )
          window.close()
        }
        window.addEventListener("message", receiveMessage, false)
        window.opener.postMessage("authorizing:github", "*")
      })()
    </script></body></html>`)
  } catch (err) {
    res.status(500).send('OAuth exchange failed: ' + err.message)
  }
}
