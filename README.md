# BloodHound CLI

A CLI tool to interact with the [BloodHound CE](https://github.com/SpecterOps/BloodHound) API.

BloodHound is *the* tool to work with Active Directory attack paths, taking advantage of modeling security-relevant relationships in a graph with nodes and edges.
But once filled with data, the BloodHound database is also a great source of information useful beyond the BloodHound GUI.
A lot of information you typically dump from LDAP is already available in BloodHound.

Retrieve lists of user names for further processing, grep in the description field, or even run custom Cypher queries, `bhcli` makes the information accessible on the commandline.
Oh and it can ingest ZIP files!

I implemented basic features I often need first, with probably more to follow.


## Installation

This tool is not published on PyPi yet, but as with any Python tool, just fetch the repository and install it.
For example using a virtualenv and `pip`:

```console
$ git clone https://github.com/exploide/bloodhound-cli.git
$ cd bloodhound-cli
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install .
```

Or using `pipx` which handles the virtualenv automatically:

```console
$ git clone https://github.com/exploide/bloodhound-cli.git
$ cd bloodhound-cli
$ pipx install .
```


### Tab Completion

Thanks to the Click framework, you can get tab completion for the `bhcli` command for free.
At least if your shell is bash, zsh or fish.
See the [click documentation](https://click.palletsprojects.com/en/latest/shell-completion/#enabling-completion) if you want to enable this feature.


## Usage

```console
$ bhcli --help
Usage: bhcli [OPTIONS] COMMAND [ARGS]...

  CLI tool to interact with the BloodHound CE API

Options:
  --debug     Enable debug output.
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  audit      Audit domains for potential security issues.
  auth       Authenticate to the server and configure an API token.
  computers  Get lists of computers.
  cypher     Run a raw Cypher query and print the response as JSON.
  domains    Get lists of domains.
  groups     Get lists of groups.
  stats      Get statistics on domains.
  upload     Upload and ingest files from the BloodHound collector.
  users      Get lists of users.
```

Passing `-h` to any of the subcommands will show the usage for the specific subcommand.


### auth

The `auth` subcommand is used to do the initial authentication to the BloodHound server, create a new API token and store it in the config file.
The config file is by default located at `$HOME/.config/bhcli/bhcli.ini` but respects `$XDG_CONFIG_HOME`.

```console
$ bhcli auth http://localhost:8080
Username: admin
Password:
INFO: Authenticating to the BloodHound server...
INFO: Creating new API token...
INFO: Storing API token to config file: /home/user/.config/bhcli/bhcli.ini
INFO: bhcli is now configured and ready to access the API.
```


### upload

The `upload` subcommand can be used to ingest data from JSON or ZIP files into the BloodHound database.

```console
$ bhcli upload *.zip
INFO: Starting new file upload job...
INFO: Processing ZIP file 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_computers.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_users.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_groups.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_containers.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_domains.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_gpos.json from 20231022025250_BloodHound.zip
INFO: Uploading file 20231022025250_ous.json from 20231022025250_BloodHound.zip
INFO: Ending file upload job...
INFO: Now waiting for ingestion being complete...
INFO: Ingestion completed, the data is now available.
```


### domains

The `domains` subcommand outputs the domains known to BloodHound.

```console
$ bhcli domains --sid
DEV.CONTOSO.COM	S-1-5-21-3196737421-3229850471-3263425470
CONTOSO.COM	S-1-5-21-1625355769-4140374492-270706875
```


### users

The `users` subcommand outputs lists of user objects.

```console
$ bhcli users --domain dev.contoso.com --enabled --description
ADMINISTRATOR@DEV.CONTOSO.COM	Built-in account for administering the computer/domain
APACHESVC@DEV.CONTOSO.COM
JULIA@DEV.CONTOSO.COM
SQLSVC01@DEV.CONTOSO.COM
```


### computers

The `computers` subcommand outputs lists of computer objects.

```console
$ bhcli computers --domain dev.contoso.com --sam
DC02.DEV.CONTOSO.COM	DC02$
WEB06.DEV.CONTOSO.COM	WEB06$
```


### groups

The `groups` subcommand outputs lists of group objects.

```console
$ bhcli groups
ACCESS CONTROL ASSISTANCE OPERATORS@DEV.CONTOSO.COM
ACCOUNT OPERATORS@DEV.CONTOSO.COM
ADMINISTRATORS@DEV.CONTOSO.COM
ALLOWED RODC PASSWORD REPLICATION GROUP@DEV.CONTOSO.COM
```


### stats

The `stats` subcommand is useful to get a statistical overview about the domain.

```console
$ bhcli stats -d contoso.com
┌────────────────────┬─────────┬─────────┐
│ CONTOSO.COM        │   all   │ enabled │
├────────────────────┼─────────┼─────────┤
│ User accounts      │      10 │       7 │
│ Computer accounts  │       6 │       6 │
│ Domain admins      │       2 │       2 │
│ Domain controllers │       1 │       1 │
│ Protected users    │       0 │       0 │
│ Groups             │      58 │         │
└────────────────────┴─────────┴─────────┘
```


### audit

The `audit` subcommand reports potential security issues within the domain, which might lead to a quick win.

```console
$ bhcli audit -d contoso.com
CONTOSO.COM
=========

[*] Kerberoastable user accounts of high value (enabled)
    1 accounts found
ADMINISTRATOR@CONTOSO.COM

[*] AS-REP-roastable user accounts (enabled)
    1 accounts found
JOHN@CONTOSO.COM

[*] Accounts trusted for unconstrained delegation (enabled, no DCs)
    1 accounts found
APPSRV02.CONTOSO.COM
```


### cypher

The `cypher` subcommand lets you directly run a Cypher query against the database.
It outputs JSON data which can be further processed, e.g. with `jq`.

```console
$ bhcli cypher 'MATCH (c:Computer) RETURN c' | jq -c '.nodes[].properties | [.name, .haslaps]'
["WEB06.DEV.CONTOSO.COM",true]
["DC02.DEV.CONTOSO.COM",false]
```
