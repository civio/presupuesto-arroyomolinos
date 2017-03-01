# -*- coding: UTF-8 -*-
import datetime

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

class ArroyomolinosPaymentsLoader(PaymentsLoader):

    # Parse an input line into fields
    def parse_item(self, budget, line):

        policy_id = line[1].strip()[:2] # First two digits of the programme make the policy id
        # But what we want as area is the policy description
        policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

        # We need to limit the length of the descriptions, they're way over the limit
        description = unicode(line[6].strip(), encoding='utf8')[:300]

        # Flag items as anonymized or not, so they don't show in the list of biggest providers
        payee = self._titlecase(line[5].strip())
        anonymized = payee.startswith('Este concepto recoge')

        return {
            'area': policy,
            'programme': None,
            'fc_code': None,  # We don't try (yet) to have foreign keys to existing records
            'ec_code': None,
            'date': datetime.datetime.strptime(line[3].strip(), "%d/%m/%Y"),
            'contract_type': None,
            'payee': payee,
            'anonymized': anonymized,
            'description': description,
            # The Excel files are inconsistent, in2csv renders different number formats (?!)
            'amount': self._read_english_number(line[7]) if budget.year==2016 else self._read_spanish_number(line[7])
        }
