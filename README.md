# BloodHound CLI

A CLI tool to interact with the [BloodHound CE](https://github.com/SpecterOps/BloodHound) API.

BloodHound by SpecterOps is *the* tool to work with Active Directory attack paths, taking advantage of modeling security-relevant relationships in a graph with nodes and edges.

Once filled with data, the BloodHound database is also a great source of information useful beyond the BloodHound GUI.
A lot of information you typically dump from LDAP is already available in BloodHound.
`bhcli` makes this information accessible on the commandline.
Retrieve lists of user names for further processing, grep in the description field, or even run custom Cypher queries.

`bhcli` can also mark a bunch of objects as owned, import/export your custom queries and might perform an audit to search for interesting permissions.
Check the help message below for all features.

> [!IMPORTANT]
> Do **not** confuse it with [bloodhound-cli by SpecterOps](https://github.com/SpecterOps/bloodhound-cli) which serves another purpose and is used to start a containerized BloodHound CE instance and configure it.
> Unfortunately, both tools share the project name bloodhound-cli, but SpecterOps' installs as `bloodhound-cli` while my project here installs as `bhcli`.


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
Check it out, everything is 3x more awesome with tab completions!


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
  mark       Mark objects as belonging to an asset group.
  members    Get lists of group members.
  queries    Import and export custom queries.
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
INFO: Uploading file 20240404165636_BloodHound.zip
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
...
```


### computers

The `computers` subcommand outputs lists of computer objects.

```console
$ bhcli computers --domain dev.contoso.com --sam
DC02.DEV.CONTOSO.COM	DC02$
WEB06.DEV.CONTOSO.COM	WEB06$
...
```


### groups

The `groups` subcommand outputs lists of group objects.

```console
$ bhcli groups
ACCESS CONTROL ASSISTANCE OPERATORS@DEV.CONTOSO.COM
ACCOUNT OPERATORS@DEV.CONTOSO.COM
ADMINISTRATORS@DEV.CONTOSO.COM
ALLOWED RODC PASSWORD REPLICATION GROUP@DEV.CONTOSO.COM
...
```


### members

The `members` subcommand outputs lists of group members.

```console
$ bhcli members --indirect 'DOMAIN ADMINS@DEV.CONTOSO.COM'
ADMINISTRATOR@DEV.CONTOSO.COM
JULIA@DEV.CONTOSO.COM
...
```


### stats

The `stats` subcommand is useful to get a statistical overview about the domain.

```console
$ bhcli stats -d contoso.com
┌────────────────────┬─────────┬─────────┐
│ CONTOSO.COM        │   all   │ enabled │
├────────────────────┼─────────┼─────────┤
│ User Accounts      │      40 │      25 │
│ Computer Accounts  │      11 │      10 │
│ Domain Admins      │       4 │       3 │
│ Domain Controllers │       1 │       1 │
│ Protected Users    │       0 │       0 │
│ Groups             │      84 │         │
│ Root CAs           │       1 │         │
│ Enterprise CAs     │       2 │         │
│ Cert Templates     │      43 │         │
└────────────────────┴─────────┴─────────┘
```


### audit

The `audit` subcommand reports potential security issues within the domain, which might lead to a quick win.

```console
$ bhcli audit -d contoso.com
CONTOSO.COM
=========

[*] Interesting privileges for domain users or computers
    2 relations found
Group                                  Relation            Target                  Kind of Target
AUTHENTICATED USERS@CONTOSO.COM        ADCSESC1            CONTOSO.COM             Domain
EVERYONE@CONTOSO.COM                   GenericWrite        JANE@CONTOSO.COM        User

[*] Interesting privileges for guests
    0 relations found

[*] Kerberoastable user accounts of high value (enabled, no MSA/gMSA)
    1 accounts found
ADMINISTRATOR@CONTOSO.COM

[*] AS-REP-roastable user accounts (enabled)
    1 accounts found
JOHN@CONTOSO.COM

[*] Accounts trusted for unconstrained delegation (enabled, no DCs)
    1 accounts found
APPSRV02.CONTOSO.COM
```


### mark

The `mark` subcommand allows to mark a bunch of user and computer objects as belonging to an asset group.
BloodHound comes with the asset groups `owned` and `admin_tier_0` by default, but custom groups can be created, too.

```console
$ bhcli mark owned --file successful_password_spraying.txt
INFO: Marked 6 objects as owned.
```


### queries

The `queries` subcommand allows to import and export custom Cypher queries.
The import file must either be in the format that the `--save` option produces or in the legacy Bloodhound's `customqueries.json` format.
Note that not everything from the latter might be compatible.

```console
$ bhcli queries my-bloodhound-queries.json
INFO: Imported 12 custom queries.
```


### cypher

The `cypher` subcommand lets you directly run a Cypher query against the database.
It outputs JSON data which can be further processed, e.g. with `jq`.

```console
$ bhcli cypher 'MATCH (c:Computer) RETURN c' | jq -c '.nodes[].properties | [.name, .haslaps]'
["WEB06.DEV.CONTOSO.COM",true]
["DC02.DEV.CONTOSO.COM",false]
```
