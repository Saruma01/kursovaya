    def generate_board(self):
        # Создаем пары значений (каждое значение должно встречаться ровно дважды)
        values = [i % (len(card_images) // 2) for i in range(self.total_pairs * 2)]
        random.shuffle(values)
        
        # Создаем карточки с перемешанными значениями
        self.cards = []
        for i in range(self.rows * self.cols):
            row = i // self.cols
            col = i % self.cols
            self.cards.append(Card(values[i], row, col))