```yaml
- !Class
    symbol:
      !Symbol {token: B}
    decorators:
      - !Decorator
          symbol:
            !Symbol {token: deco}
          arguments:
            - !Argument
                value:
                  !Symbol {token: arg1}
    parents:
      - !Symbol {token: A}
    block:
      !Block
        statements:
          - 

```
