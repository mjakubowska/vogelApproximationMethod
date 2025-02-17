from operator import attrgetter
from writeFile.Deal import Deal
from writeFile.Configuration import Configuration


def find_2min_diff(min_list):
    if len(min_list) <= 1:
        return 0
    min1 = min(min_list[0].price, min_list[1].price)
    min2 = max(min_list[0].price, min_list[1].price)
    for x in min_list[2::]:
        if x.price <= min1:
            min1, min2 = x.price, min1
        elif x.price < min2:
            min2 = x.price
    return round(min2 - min1, 2)


class Vogel:
    def __init__(self, loader):
        self.matrix = []
        self._min_r = []
        self._min_c = []
        self._loader = loader
        self.solution = Configuration()

    def load_contracts(self):
        contracts = self._loader.contracts
        rows = len(self._loader.pharmacies)
        for producers in range(rows):
            self.matrix.insert(producers, contracts[producers])
        self._find_mins()

    def create_configuration(self):
        while len(self.matrix) > 0:
            self.fill_pharmacy()

    def print_matrix(self):
        for i in range(len(self.matrix)):
            print(self.matrix[i])

    def _find_mins(self):
        try:
            for rows in self.matrix:
                self._min_r.append(find_2min_diff(rows))
        except IndexError:
            print("Macierz jest pusta")
        else:
            for columns in range(len(self.matrix[0])):
                column = []
                for rows in range(len(self.matrix)):
                    column.append(self.matrix[rows][columns])
                self._min_c.append(find_2min_diff(column))

    def update_rows_mins(self):
        if len(self.matrix) < 1:
            return
        self._min_r = []
        for rows in self.matrix:
            self._min_r.append(find_2min_diff(rows))

    def update_columns_mins(self):
        if len(self.matrix) < 1:
            return
        if len(self.matrix[0]) < 1:
            return
        self._min_c = []
        for columns in range(len(self.matrix[0])):
            column = []
            for rows in range(len(self.matrix)):
                column.append(self.matrix[rows][columns])
            self._min_c.append(find_2min_diff(column))

    def find_max_mins(self):
        value_c = max(self._min_c)
        value_r = max(self._min_r)
        if value_c > value_r:
            index_c = self._min_c.index(value_c)
            index_r = self.matrix.index(min(self.matrix, key=lambda x: x[index_c].price))
        else: # value_r >= value_c
            index_r = self._min_r.index(value_r)
            index_c = self.matrix[index_r].index(min(self.matrix[index_r], key=attrgetter('price')))
        return index_r, index_c #, index_r #row-dostawca, #column-apteka

    def fill_pharmacy(self):
        index_r, index_c = self.find_max_mins()
        contract = self.matrix[index_r][index_c]
        id_pr = self.matrix[index_r][index_c].id_pr
        id_ph = self.matrix[index_r][index_c].id_ph
        pharmacy = self._loader.pharmacies[id_ph]
        while self._loader.pharmacies[id_ph] != 0:
            producer = self._loader.producers[id_pr]
            if pharmacy.amount <= producer.amount:
                if pharmacy.amount > contract.amount:
                    deal_amount = contract.amount
                else:
                    deal_amount = pharmacy.amount
                deal = Deal(producer, pharmacy, deal_amount, contract.price)
                self.solution.deals.append(deal)
                self.solution.cost += round(deal_amount * contract.price, 2)
                self._loader.producers[id_pr].amount -= deal_amount
                self._loader.pharmacies[id_ph].amount -= deal_amount
                self.matrix[index_r][index_c].amount -= deal_amount
                if self.matrix[index_r][index_c].amount == 0:
                    del self.matrix[index_r][index_c]
                if self._loader.producers[id_pr].amount == 0:
                    for i in range(len(self.matrix)):
                        del self.matrix[i][index_c]
                    del self._min_c[index_c]
                    self.update_rows_mins()
                if self._loader.pharmacies[id_ph].amount == 0:
                    del self.matrix[index_r]
                    del self._min_r[index_r]
                    self.update_columns_mins()
                    break
            elif pharmacy.amount > producer.amount:
                if producer.amount > contract.amount:
                    deal_amount = contract.amount
                else:
                    deal_amount = producer.amount
                deal = Deal(producer, pharmacy, deal_amount, contract.price)
                self.solution.deals.append(deal)
                self.solution.cost += round(deal_amount * contract.price, 2)
                self._loader.producers[id_pr].amount -= deal_amount
                self._loader.pharmacies[id_ph].amount -= deal_amount
                self.matrix[index_r][index_c].amount -= deal_amount
                if self.matrix[index_r][index_c].amount == 0:
                    del self.matrix[index_r][index_c]
                if producer.amount == 0:
                    for i in range(len(self.matrix)):
                        del self.matrix[i][index_c]
                    del self._min_c[index_c]
                    self.update_rows_mins()
            if len(self.matrix[index_r]) == 0:
                raise ValueError(f"Nie udało się zapełcić aptek")
            index_c = self.matrix[index_r].index(min(self.matrix[index_r], key=attrgetter('price')))
            contract = self.matrix[index_r][index_c]
            id_pr = self.matrix[index_r][index_c].id_pr

    def get_min_c(self):
        return self._min_c

    def get_min_r(self):
        return self._min_r


