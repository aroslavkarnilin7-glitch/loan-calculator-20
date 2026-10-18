import math
import tkinter as tk
from tkinter import ttk

import api
import db


class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Калькулятор кредита с конвертацией валют")
        self.geometry("760x650")

        self.monthly_payment = None

        self.create_widgets()
        db.init_db()
        self.log("Приложение запущено. База данных инициализирована.")

    def create_widgets(self) -> None:
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        self.loan_var = tk.StringVar(value="1000000")
        self.loan_time_var = tk.StringVar(value="12")
        self.annual_interest_var = tk.StringVar(value="10")
        self.base_var = tk.StringVar(value="RUB")
        self.target_var = tk.StringVar(value="USD")

        ttk.Label(main_frame, text="Сумма кредита (RUB):").grid(
            row=0, column=0, sticky="w", pady=4
        )
        ttk.Entry(main_frame, textvariable=self.loan_var).grid(
            row=0, column=1, sticky="ew", pady=4
        )

        ttk.Label(main_frame, text="Срок кредита (мес.):").grid(
            row=1, column=0, sticky="w", pady=4
        )
        ttk.Entry(main_frame, textvariable=self.loan_time_var).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(main_frame, text="Годовая процентная ставка (%):").grid(
            row=2, column=0, sticky="w", pady=4
        )
        ttk.Entry(main_frame, textvariable=self.annual_interest_var).grid(
            row=2, column=1, sticky="ew", pady=4
        )

        ttk.Button(
            main_frame,
            text="Рассчитать кредит",
            command=self.calculate_loan,
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)

        self.monthly_label = ttk.Label(main_frame, text="Ежемесячный платёж: —")
        self.monthly_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=2)

        self.loan_sum_label = ttk.Label(main_frame, text="Сумма всех платежей: —")
        self.loan_sum_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=2)

        self.interest_label = ttk.Label(main_frame, text="Начисленные проценты: —")
        self.interest_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Separator(main_frame, orient="horizontal").grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=10
        )

        ttk.Label(main_frame, text="Начальная валюта:").grid(
            row=8, column=0, sticky="w", pady=4
        )
        ttk.Label(main_frame, textvariable=self.base_var).grid(
            row=8, column=1, sticky="w", pady=4
        )

        ttk.Label(main_frame, text="Искомая валюта:").grid(
            row=9, column=0, sticky="w", pady=4
        )
        self.target_entry = ttk.Combobox(
            main_frame,
            textvariable=self.target_var,
            values=["USD", "EUR", "CNY", "GBP", "JPY"],
            state="readonly",
        )
        self.target_entry.grid(row=9, column=1, sticky="ew", pady=4)

        ttk.Button(
            main_frame,
            text="Конвертировать ежемесячный платёж",
            command=self.convert,
        ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=8)

        self.result_label = ttk.Label(main_frame, text="Результат конвертации: —")
        self.result_label.grid(row=11, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Button(
            main_frame,
            text="Обновить курсы валют",
            command=self.update_db,
        ).grid(row=12, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(main_frame, text="Лог действий:").grid(
            row=13, column=0, columnspan=2, sticky="w", pady=(8, 2)
        )

        self.log_text = tk.Text(main_frame, height=10, state="disabled")
        self.log_text.grid(row=14, column=0, columnspan=2, sticky="nsew")

        main_frame.rowconfigure(14, weight=1)

    def log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def is_loan_invalid(self, value: float, message: str) -> bool:
        if value <= 0:
            self.log(message)
            return True
        return False

    def calculate_loan(self) -> None:
        try:
            loan = float(self.loan_var.get().replace(" ", "").replace(",", "."))
            months = int(float(self.loan_time_var.get().replace(",", ".")))
            annual_interest = float(self.annual_interest_var.get().replace(",", "."))
        except ValueError:
            self.log("Ошибка: введите корректные числовые значения.")
            return

        if self.is_loan_invalid(loan, "Сумма кредита должна быть больше 0."):
            return
        if self.is_loan_invalid(months, "Срок кредита должен быть больше 0."):
            return
        if self.is_loan_invalid(
            annual_interest, "Процентная ставка должна быть больше 0."
        ):
            return

        monthly_rate = annual_interest / 12 / 100
        monthly_payment = (
            loan * monthly_rate / (1 - math.pow(1 + monthly_rate, -months))
        )
        total_sum = monthly_payment * months
        interest = total_sum - loan

        self.monthly_payment = monthly_payment

        self.monthly_label.config(
            text=f"Ежемесячный платёж: {monthly_payment:,.2f} RUB".replace(",", " ")
        )
        self.loan_sum_label.config(
            text=f"Сумма всех платежей: {total_sum:,.2f} RUB".replace(",", " ")
        )
        self.interest_label.config(
            text=f"Начисленные проценты: {interest:,.2f} RUB".replace(",", " ")
        )

        self.log("Кредит успешно рассчитан.")

    def convert(self) -> None:
        if self.monthly_payment is None:
            self.log("Сначала рассчитайте кредит.")
            return

        target_currency = self.target_var.get().strip().upper()

        if not target_currency:
            self.log("Выберите валюту для конвертации.")
            return

        try:
            if target_currency == "RUB":
                converted = self.monthly_payment
            else:
                rate = db.get_saved_rate(target_currency)

                if rate is None or rate <= 0:
                    self.log(
                        f"Курс {target_currency} не найден. "
                        "Нажмите «Обновить курсы валют»."
                    )
                    return

                converted = self.monthly_payment / rate

            self.result_label.config(
                text=(
                    f"{self.monthly_payment:,.2f} RUB = "
                    f"{converted:,.2f} {target_currency}"
                ).replace(",", " ")
            )

            self.log(f"Конвертация выполнена: RUB → {target_currency}.")
        except Exception as error:
            self.log(f"Ошибка при конвертации: {error}")

    def update_db(self) -> None:
        try:
            data = api.fetch_rates()
            valute = data.get("Valute", {})

            if not valute:
                self.log("API не вернул данные о валютах.")
                return

            codes = []

            for index, (code, info) in enumerate(valute.items(), start=1):
                nominal = float(info.get("Nominal", 1))
                value = float(info["Value"])
                rate = value / nominal

                db.save_rate(index, code, rate)
                codes.append(code)

            values = ["RUB"] + sorted(codes)
            self.target_entry.configure(values=values)

            current_currency = self.target_var.get()
            if current_currency not in values:
                self.target_var.set("USD" if "USD" in values else values[0])

            self.log(f"Курсы обновлены. Загружено валют: {len(codes)}.")

        except Exception as error:
            self.log(f"Ошибка обновления курсов: {error}")


if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()