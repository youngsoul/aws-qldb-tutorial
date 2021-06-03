
# Tutorial

https://docs.aws.amazon.com/qldb/latest/developerguide/what-is.html

fork of:

 https://github.com/aws-samples/amazon-qldb-dmv-sample-python.git


# ChangeLog

- Change create_ledger.py to use Session with profile

- Change create_ledger call to set DeletionProtection to False

- remove pysqldbcommands from pacakge path in create_ledger.py

- EVERYWHERE, create a Session with the correct profile

# Commands

```python
python pyqldbsamples/create_ledger.py

python pyqldbsamples/connect_to_ledger.py

python pyqldbsamples/create_table.py

python pyqldbsamples/create_index.py

python pyqldbsamples/insert_document.py
```
