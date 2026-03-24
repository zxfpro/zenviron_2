# Skill Install And Version Check

When `npx skills add zxfpro/zenviron_2 --skill <name> -y` times out (60s clone timeout), use local-path install.

## Recommended (Most Stable)

```bash
# 1) Clone once to local disk
git clone --depth 1 https://github.com/zxfpro/zenviron_2.git ~/GitHub/zenviron_2

# 2) Install skills from local path (no remote clone in skills CLI)
npx skills add ~/GitHub/zenviron_2 --skill monorepo -y
npx skills add ~/GitHub/zenviron_2 --skill sql-docker -y
```

## If HTTPS Is Slow, Use SSH

```bash
git clone --depth 1 git@github.com:zxfpro/zenviron_2.git ~/GitHub/zenviron_2
npx skills add ~/GitHub/zenviron_2 --skill monorepo -y
npx skills add ~/GitHub/zenviron_2 --skill sql-docker -y
```

## Update To Latest

```bash
cd ~/GitHub/zenviron_2
git pull --ff-only
npx skills add ~/GitHub/zenviron_2 --skill monorepo -y
npx skills add ~/GitHub/zenviron_2 --skill sql-docker -y
```

## Verify Installed Version

```bash
cat ~/.agents/skills/monorepo/VERSION.md
cat ~/.agents/skills/sql-docker/VERSION.md
```

Expected current version: `0.2.4`
