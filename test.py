#encoding:utf8

if __name__ == "__main__":
    from unittest import TestLoader, TextTestRunner
    import test.tests
    with test.tests.TestContext() as context: 
        TextTestRunner(verbosity=2).run(TestLoader().loadTestsFromModule(test.tests)) 
