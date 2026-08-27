from app.services.synthetic.generator import DataGenerator
gen = DataGenerator(seed=1)
o, p, s, b, gt = gen.gen_exact_match("SCN-1")
print(p[0].amount, s[0].gross_amount, s[0].fee)
