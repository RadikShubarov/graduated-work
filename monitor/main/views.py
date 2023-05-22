import os
import numpy as np
import pandas as pd
import re

from django.shortcuts import render
from .models import Host, SarData, PcaPeaks
from django.views.generic import DetailView
from scipy.signal import find_peaks
from sklearn.decomposition import PCA
from .forms import LogForm, HostForm
from django.http import HttpResponseRedirect
from datetime import datetime
import pytz


def start(request):
    return HttpResponseRedirect('main')  # REDIRECT TO MAIN


def index(request):
    error = ''
    curr_host = ''
    date = ''
    src = ''
    src_pca = ''
    result = []
    log_form = LogForm()
    host_form = HostForm()
    if request.method == 'POST':
        log_form = LogForm(request.POST)
        host_form = HostForm(request.POST)
        if log_form.is_valid() and host_form.is_valid():
            dir_path = 'main/static/main/date_log_img'
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))
            date = log_form.cleaned_data['log_time']
            host = host_form.cleaned_data['host']
            curr_host = Host.objects.get(host=host)
            sar = SarData.objects.filter(log_time=date, host_machine=curr_host)
            df = format_to_df(sar)
            if not df.empty:
                draw_main_graph(df, f'main/static/main/date_log_img/{curr_host}_{date}')
                src = 'main/static/main/date_log_img/{curr_host}_{date}_main.png'
                get_pca(df, f'main/static/main/date_log_img/{curr_host}_{date}')
                src_pca = 'main/static/main/date_log_img/{curr_host}_{date}_pca.png'
                peak_by_time = PcaPeaks.objects.filter(host_owner=curr_host, log_times=date)
                for pca_peak in peak_by_time:
                    if pca_peak.danger_prediction:
                        pca_peak.danger_prediction = 'Нестабильные показатели!'
                    else:
                        pca_peak.danger_prediction = 'Стабильные показатели!'
                peak_data = [peak.peak for peak in peak_by_time] + [peak.danger_prediction for peak in peak_by_time]
                for i in range(len(peak_data) // 2):
                    value = peak_data[i]
                    status = peak_data[i + len(peak_data) // 2]
                    formatted_value = f"{value} - {status}"
                    result.append(formatted_value)
            else:
                error = 'В это время нет статистики!'

        else:
            error = 'Поля заполнены неверно!'
    data = {'log_form': log_form,
            'host_form': host_form,
            'error': error,
            'host': curr_host,
            'date': date,
            'img_src': src,
            'img_src_pca': src_pca,
            'peak_time': result
            }

    check_hosts()
    return render(request, 'main/index.html', data)


class HostDetailView(DetailView):
    model = Host
    template_name = 'main/host_layout.html'
    context_object_name = 'server_name'
    slug_field = 'host'
    slug_url_kwarg = 'host'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('host')
        curr_host = Host.objects.get(host=pk)
        ddf = check_sar_data(curr_host)
        sar = SarData.objects.filter(host_machine=curr_host)
        df = format_to_df(sar)
        if not df.empty:
            draw_main_graph(df, f'main/static/main/{curr_host}')
            # context['sar'] = df
            context['mail'] = 'Стабильные показатели!'
            pca_res = get_pca(df, f'main/static/main/{curr_host}')
            # if ddf is not None:
            #     if not ddf.empty:
            #         df_pca = ddf
            #         df_pca.dropna(inplace=True)
            #         pca = PCA(n_components=1)
            #         res = pca.fit_transform(df_pca)
            #         min_value = np.amin(res)
            #         res = res + abs(min_value)
            #         max_curr_peak = round(find_max_peaks(res), 2)
            #         context['curr_peak'] = max_curr_peak
            max_peak = round(find_max_peaks(pca_res), 2)
            context['peak'] = max_peak
            is_danger = check_peaks(max_peak, curr_host)
            if is_danger:
                context['mail'] = 'Нестабильные показатели!'
        return context


def check_hosts():
    all_hosts = Host.objects.all()
    for el in all_hosts:
        if not SarData.objects.filter(host_machine=el).exists():
            Host.objects.filter(host=el).delete()

    dir_path = 'main/static/main/sarlogs'
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            with open(os.path.join(dir_path, file)) as f:
                content = f.readline()
                content = re.split('\s+', content)
                host = content[2][1:-1]
            if not Host.objects.filter(host=host).exists():
                add_host = Host(host=host)
                add_host.save()


def check_sar_data(host_m):
    dir_path = 'main/static/main/sarlogs'
    for file in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file)):
            with open(os.path.join(dir_path, file)) as f:
                content = f.readline()
                content = re.split('\s+', content)
                host = content[2][1:-1]
                if host != str(host_m):
                    f.close()
                    return
                log_time = content[3]
                sar_content = f.readlines()
            if not Host.objects.filter(host=host).exists():
                add_host = Host(host=host)
                add_host.save()
            sar_content = [x.strip() for x in sar_content]
            sar_content = [x.replace(',', '.') for x in sar_content]
            sar_content = [x.split() for x in sar_content]
            sar_content = sar_content[2:-1]
            # VAAAAAAAAAAAAAAAAAAAAAAAA
            df = pd.DataFrame(sar_content[1:], columns=sar_content[0])
            df.columns.values[0] = 'time'
            df.drop(['all'], axis=1, inplace=True)
            df = df.set_index('time')
            df = df.astype('float')
            #AAAAAAAAAAAAAAAAAAAAAAAAAAA
            host_m = Host.objects.get(host=host)
            for row in sar_content:
                insert_sar_log = SarData(log_time=log_time, time=row[0], user=row[2], nice=row[3], system=row[4],
                                         iowait=row[5], steal=row[6], host_machine=host_m)
                insert_sar_log.save()

            os.remove(os.path.join(dir_path, file))
            return df

def format_to_df(data):
    values_list = list(data.values())
    time_index = [x['time'] for x in values_list]
    df = pd.DataFrame.from_records(values_list, index=time_index)
    if not df.empty:
        df.drop(['id'], axis=1, inplace=True)
        df = df.set_index('time')
    return df


def draw_main_graph(data, src):
    data.drop(['host_machine_id'], axis=1, inplace=True)
    data.drop(['log_time'], axis=1, inplace=True)
    data = data.astype('float')
    graph = data.plot().get_figure()
    graph.savefig(f'{src}_main.png')


def draw_pca_graph(data, src):
    graph = data.plot()
    graph.lines[0].set_label('pca line')
    graph.legend()
    graph.figure.savefig(f'{src}_pca.png')


def get_pca(df_data, src):
    df_pca = df_data
    df_pca.dropna(inplace=True)
    pca = PCA(n_components=1)
    res = pca.fit_transform(df_pca)
    min_value = np.amin(res)
    res = res + abs(min_value)
    pca_df = pd.DataFrame(data=res, index=df_pca.index)
    # pca_min_df = pca_df.min(axis=0)
    # pca_df = pca_df + abs(pca_min_df)
    draw_pca_graph(pca_df, src)
    return res


def find_max_peaks(pca_res):
    one_d = pca_res.ravel()
    peaks, _ = find_peaks(one_d, height=0)
    i_max_peak = peaks[np.argmax(one_d[peaks])]
    x_max = one_d[i_max_peak]
    return x_max


def check_peaks(peak, host):
    warnings_flag: bool = False
    timezone = pytz.timezone("Europe/Moscow")
    current_datetime = datetime.now(tz=timezone).strftime('%d.%m.%Y')
    owner_peaks = PcaPeaks.objects.filter(host_owner=host)
    peak_df = pd.DataFrame.from_records(owner_peaks.values())
    if not peak_df.empty:
        peak_mean = peak_df['peak'].mean()
        dif = peak / peak_mean
        if dif >= 1.5:
            warnings_flag = True
        if not PcaPeaks.objects.filter(peak=peak, host_owner=host, log_times=current_datetime, danger_prediction=warnings_flag).exists():
            add_peak = PcaPeaks(peak=peak, host_owner=host, log_times=current_datetime, danger_prediction=warnings_flag)
            add_peak.save()
    else:
        add_peak = PcaPeaks(peak=peak, host_owner=host, log_times=current_datetime, danger_prediction=warnings_flag)
        add_peak.save()
    return warnings_flag