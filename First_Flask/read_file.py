import pandas as pd
import os
import csv
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

def get_delimiter(path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def read_csv(path):
    #path = request.files['path']
    delimiter = get_delimiter(path)
    df = pd.read_csv(path,delimiter=delimiter)
    return df

def html_style(df):
    df=df.replace('<th>','<th scope="col">')
    df=df.replace('<tr>','<tr class="table-primary">')
    df=df.replace('"dataframe data"','"table table-hover"')
    return df

if __name__ == "__main__":
    path = r"D:\Learn\Python\backup_android_budget\Compte Courant-20230324-182003.csv"
    df = read_csv(path)
    print(html_style(df.to_html(classes="data", header="true")))
    print(df.columns)
