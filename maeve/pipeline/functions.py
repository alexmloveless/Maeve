import inspect
from typing import Union


class FunctionPipeline:

    def __init__(self, session):
        self.s = session

    def run_pipeline(self, conf: Union[dict, list, str], obj=None):
        if type(conf) is dict:
            # keys are only there to help manage the order of funcs
            conf = conf.values()
        elif type(conf) is str:
            # assume it's a reference to a pipeline conf
            pass
        else:
            raise ValueError("Unknown data type for pipeline conf")

        for f in conf:
            obj = self.run_func(obj, conf)

    def run_func(self, obj=None, attrs=None):
        args = attrs.get("args", [])
        kwargs = attrs.get("kwargs", {})

        try:
            func = getattr(self, attrs['function'])
        except AttributeError:
            raise AttributeError("No function in namespace called: {}".format(attrs['function']))

        sig = inspect.signature(func)
        if "obj" not in sig.parameters:
            try:
                func(*args, **kwargs)
                return obj
            except Exception as e:
                _ = self.handle_func_fail(attrs, e)
                return obj
        else:
            try:
                return func(obj, *args, **kwargs)
            except Exception as e:
                _ = self.handle_func_fail(attrs, e)
                return obj


    def handle_func_fail(self, attrs, e, ret=None):
        if attrs.get("fail_silently", False):
            self.log.info(
                "Marty pipeline function {} failed with error {}".format(attrs['function'], e)
            )
            return ret
        else:
            raise RuntimeError("Marty pipeline function {} failed".format(attrs['function'])) from e