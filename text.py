import pygame

class Text:
    def __init__(self, text, size, rect):
        self.font = pygame.font.Font('data/pokemonemerald.ttf', size)
        self.text_array = text.split()
        self.rect = rect
        self.row_width = rect.width
        self.row_height = self.font.size('Tg')[1]
        self.rows = int(rect.height / self.row_height)

    def render(self, screen):
        texts = self.text_array
        r = 0
        remaining_width = self.row_width
        for text in texts:
            working_text = text + ' '
            text_width = self.font.size(working_text)[0]
            if text == 'nl':
                r+=1
                remaining_width = self.row_width
            else:
                if text_width < remaining_width:
                    screen.blit(self.font.render(text, True, (255,255,255)), (self.row_width - remaining_width,self.rect.top + r * self.row_height))
                    remaining_width -= text_width
                else:
                    remaining_width = self.row_width
                    r += 1
                    screen.blit(self.font.render(text, True, (255,255,255)), (self.rect.width - remaining_width,self.rect.top + r * self.row_height))
                    remaining_width -= text_width
            # print(f'x:{self.row_width}')
            # screen.blit(self.font.render(text, True, (255,255,255)), (0,0))

    def update_text(self, text):
        self.text_array = text.split()

                


