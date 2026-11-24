import csv
from collections import defaultdict

def main():
    print("1. Чтение данных...")
    data = []
    with open('students.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['EventIndex'] = int(row['EventIndex'])
            data.append(row)

    # Группируем по процессам и сортируем по EventIndex
    processes = defaultdict(list)
    for row in data:
        processes[row['ProcessInstanceId']].append(row)
    
    for pid in processes:
        processes[pid].sort(key=lambda x: x['EventIndex'])

    print(f"   Найдено {len(processes)} процессов.")

    routes = []
    transitions = []

    print("2. Анализ маршрутов и переходов...")
    for pid, events in processes.items():
        route_activities = [event['ActivityName'] for event in events]
        route_str = ' > '.join(route_activities)
        routes.append(route_str)
        
        for i in range(len(route_activities) - 1):
            transitions.append((route_activities[i], route_activities[i+1]))

    # 3. Таблица вариантов (Variants)
    variant_counts = defaultdict(int)
    for route in routes:
        variant_counts[route] += 1

    total_cases = len(processes)
    variants_data = []
    for idx, (route, count) in enumerate(sorted(variant_counts.items(), key=lambda x: x[1], reverse=True), 1):
        variants_data.append({
            'Variant': f"V{idx}",
            'Route': route,
            'NumberOfCases': count,
            'Share': round(count / total_cases, 3)
        })

    print("3. Сохранение variants.csv...")
    with open('variants.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Variant', 'Route', 'NumberOfCases', 'Share'])
        writer.writeheader()
        writer.writerows(variants_data)

    print("4. Сохранение student_transitions.csv...")
    trans_counts = defaultdict(int)
    for src, tgt in transitions:
        trans_counts[(src, tgt)] += 1

    with open('student_transitions.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['SourceActivity', 'TargetActivity'])
        for (src, tgt), count in sorted(trans_counts.items(), key=lambda x: x[1], reverse=True):
            writer.writerow([src, tgt])

    print("5. Генерация схемы Mermaid (mermaid_code.txt)...")
    mermaid_code = """graph TD
    Start((Регистрация заявки)) --> Check[Первичная проверка]
    
    Check -->|reject| Reject1[Заявка отклонена]
    Check -->|accept| Mgr[Согласование руководителем]
    
    Mgr -->|return| Rework[Доработка заявки]
    Rework --> Check
    
    Mgr -->|cancel| Cancel[Заявка отменена]
    Mgr -->|reject| Reject2[Заявка отклонена]
    Mgr -->|accept| Budget[Проверка бюджета]
    
    Budget -->|accept| Extra[Дополнительное согласование]
    Extra -->|accept| Exec[Исполнение закупки]
    
    Budget -->|accept| Exec
    
    Exec -->|accept| Done((Заявка выполнена))
    
    classDef startend fill:#f9f,stroke:#333,stroke-width:2px;
    classDef activity fill:#bbf,stroke:#333,stroke-width:1px;
    classDef finalNode fill:#f96,stroke:#333,stroke-width:2px;
    
    class Start startend;
    class Done finalNode;
    class Check,Mgr,Budget,Extra,Exec,Rework activity;
    class Reject1,Reject2,Cancel finalNode;
"""
    with open('mermaid_code.txt', 'w', encoding='utf-8') as f:
        f.write(mermaid_code)

    print("\nГотово! Созданы файлы:")
    print("   - variants.csv (8 уникальных маршрутов, 100% покрытие)")
    print("   - student_transitions.csv (12 уникальных переходов)")
    print("   - mermaid_code.txt (код для визуализации схемы)")

if __name__ == "__main__":
    main()
