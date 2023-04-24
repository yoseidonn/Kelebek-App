from flet import *

def main(page: Page):
    page.add(
        Container(
            width=280,
            height=800,
            content=Column(
                controls=[
                    TextField(
                        label='Açıklama',
                        filled=True,
                    )
                ]
            )
        )
    )


if __name__ == '__main__':
    app(target=main)
