GAMMA - Gamefication for OpenEdx.
===

GAMMA is a microservice for gamefication.
We provide REST API to work with users coins,
manage Badges or Achievements.


Usage
===
For local development
---
```
✗ npm install
✗ npm run build:dev
✗ make build
✗ make debug
```
Optionally we can use
```
✗ make dev.up env=dev
```


For staging/production usage
---
```
✗ make build
✗ make dev.up env=prod
```


Configuration
===
For docker-compose deployment `env/private.env` file can changed to pass sensitive data into container.
