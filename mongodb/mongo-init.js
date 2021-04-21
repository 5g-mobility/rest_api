// Source
// https://stackoverflow.com/a/52944387/10735382

db.auth('admin', 'admin');

db = db.getSiblingDB('5g-mobility');

db.createUser(
        {
            user: "django",
            pwd: "djangopass",
            roles: [
                {
                    role: "readWrite",
                    db: "5g-mobility"
                },
                {
                    role: "dbOwner",
                    db: "test_5g-mobility"
                },
                {
                    role: "dbOwner",
                    db: "test_5g-mobility_1"
                }
            ]
        }
);