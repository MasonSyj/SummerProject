from app import app, Attack
import csv

attacks = None
with app.app_context():
    attacks = Attack.query.all()

with open('attacks.csv', 'w') as csvfile:
    fields = ['id', 'name', 'password']
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

    for attack in attacks:
        writer.writerow({
            'id': attack.id,
            'name': attack.username,
            'password': attack.password
        })

csvfile.close()