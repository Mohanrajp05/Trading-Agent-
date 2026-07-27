from backend.accounts import Account
for name in ['Mohan', 'Rohan', 'Sohan', 'Pavan']:
    a = Account.get(name)
    print(f'{name}:')
    print(f'  balance={a.balance}')
    print(f'  holdings={dict(a.holdings)}')
    t = len(a.transactions)
    print(f'  transactions={t}')
    if a.transactions:
        last = a.transactions[-1]
        print(f'  last={last.timestamp}')
        print(f'  last_trade={last.symbol} qty={last.quantity}')
    print()
