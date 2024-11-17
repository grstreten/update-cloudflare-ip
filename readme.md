# Cloudflare Tunnel IP Watcher
Does what it says on the tin.

```
docker run -d \
  -e CLOUDFLARE_API_TOKEN="" \
  -e CLOUDFLARE_ACCOUNT_ID="" \
  -e APPLICATION_IDS="[]" \
  cloudflare-updater
```