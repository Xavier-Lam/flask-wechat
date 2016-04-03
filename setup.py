#encoding:utf8

from distutils.core import setup

setup(
	name="flask-wechat",
	packages=["flask_wechat"],
	version="0.0.1",
	author="Xavier-Lam",
	description="a simple flask module implement wechat api",
	url="https://github.com/Xavier-Lam/flask-wechat",
	install_requires=[
		"Flask==0.10.1",
		"requests==2.9.1",
	],
	keywords=["flask", "wechat", "weixin", "micromessage"],
	classifiers=[
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: Implementation",
		"Development Status :: 1 - Planning",
		"Framework :: Flask",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Natural Language :: Chinese (Simplified)",
		"Natural Language :: English",
		"Topic :: Internet :: WWW/HTTP :: Dynamic Content",
		"Topic :: Software Development :: Libraries :: Python Modules",
	]
)