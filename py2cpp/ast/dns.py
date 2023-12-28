def domainize(domain: str, *prats: str) -> str:
	return '.'.join([domain, *[part for part in prats if part]])
