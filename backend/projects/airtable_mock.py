class MockAirtableTable:
    def __init__(self):
        self._records = {}
        self._next_id = 1

    def create(self, fields):
        rec_id = f"rec{self._next_id:05d}"
        self._next_id += 1
        self._records[rec_id] = fields
        return {'id': rec_id, 'fields': fields}

    def update(self, record_id, fields):
        self._records[record_id] = fields
        return {'id': record_id, 'fields': fields}
