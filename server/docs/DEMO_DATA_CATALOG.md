# Demo Data Catalog

Run from `server`:

```powershell
python manage.py migrate
$env:DEMO_PASSWORD = "set-a-local-development-password"
python manage.py seed_demo_data
```

The command is idempotent and does not delete existing user data. On the verified development database it reported:

- Categories: 14
- Skills: 58
- Companies: 3
- Jobs: 4
- Applications: 3

Demo accounts are `demo.admin@example.com`, `demo.candidate@example.com`, and `demo.employer@example.com`. Their password is supplied only through `--password` or `DEMO_PASSWORD` and is never stored in this document.
