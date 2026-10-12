import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricecube.settings")
django.setup()

from django.urls import get_resolver

def main():
    r = get_resolver()
    def walk(patterns, prefix=""):
        for p in patterns:
            if hasattr(p, "url_patterns"):
                walk(p.url_patterns, prefix + str(p.pattern))
            else:
                print(prefix + str(p.pattern))
    walk(r.url_patterns)

if __name__ == "__main__":
    main()
