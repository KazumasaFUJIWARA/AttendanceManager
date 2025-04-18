// APIのベースURL
const API_BASE_URL = '/api';

// 曜日の日本語表記
const DAYS_OF_WEEK = ['日', '月', '火', '水', '木', '金', '土'];

// 時限の日本語表記
const PERIODS = ['', '1限', '2限', '3限', '4限', '5限', '6限'];

// ページ読み込み時に実行
document.addEventListener('DOMContentLoaded', () => {
    loadStudentData();
    // 1分ごとにデータを更新
    setInterval(loadStudentData, 60000);
    
    // コアタイムチェックボタンのイベントリスナーを設定
    const checkButtons = document.querySelectorAll('.check-coretime-btn');
    checkButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const period = button.dataset.period;
            try {
                await checkCoreTime(period);
                // 成功メッセージを表示
                alert('コアタイムチェックを実行しました。');
            } catch (error) {
                // エラーメッセージを表示
                alert('コアタイムチェックに失敗しました: ' + error.message);
            }
        });
    });
});

// 学生データの読み込み
async function loadStudentData() {
    try {
        // 学生一覧の取得
        const studentsResponse = await fetch(`${API_BASE_URL}/students/`);
        if (!studentsResponse.ok) {
            throw new Error(`学生データの取得に失敗: ${studentsResponse.status}`);
        }
        const students = await studentsResponse.json();

        // 現在の入室状況の取得
        const currentStatusResponse = await fetch(`${API_BASE_URL}/current-status/`);
        if (!currentStatusResponse.ok) {
            throw new Error(`入室状況の取得に失敗: ${currentStatusResponse.status}`);
        }
        const currentStatus = await currentStatusResponse.json();

        // 今週の日付範囲を計算
        const today = new Date();
        const startOfWeek = new Date(today);
        startOfWeek.setDate(today.getDate() - today.getDay());
        startOfWeek.setHours(0, 0, 0, 0);

        // 学生データの表示
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = '';

        for (const student of students) {
            try {
                // 現在の入室状況を確認
                const isPresent = currentStatus.some(status => status.student_id === student.student_id);
                
                // 今週の利用時間を取得
                const attendanceResponse = await fetch(`${API_BASE_URL}/attendance/${student.student_id}?days=7`);
                if (!attendanceResponse.ok) {
                    throw new Error(`出席データの取得に失敗: ${attendanceResponse.status}`);
                }
                const attendanceLogs = await attendanceResponse.json();
                
                // 利用時間の計算
                let totalHours = 0;
                for (const log of attendanceLogs) {
                    if (log.entry_time && log.exit_time) {
                        const entryTime = new Date(log.entry_time);
                        const exitTime = new Date(log.exit_time);
                        // 今週のログのみを計算
                        if (entryTime >= startOfWeek) {
                            const duration = (exitTime - entryTime) / (1000 * 60 * 60);
                            if (duration > 0) {  // 負の値は除外
                                totalHours += duration;
                            }
                        }
                    }
                }

                // コアタイムの表示形式を整形
                const coreTime1 = formatCoreTime(student.core_time_1_day, student.core_time_1_period);
                const coreTime2 = formatCoreTime(student.core_time_2_day, student.core_time_2_period);

                // 違反回数の表示を強調
                const violationClass = student.core_time_violations > 0 ? 'violation' : '';
                const violationText = student.core_time_violations > 0 ? 
                    `<span class="text-danger fw-bold">${student.core_time_violations}回</span>` : 
                    '<span class="text-muted">0回</span>';

                // テーブル行の作成
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td class="${isPresent ? 'status-present' : 'status-absent'}">
                        <span>${isPresent ? '入室中 ✓' : '退室中 ×'}</span>
                    </td>
                    <td>${totalHours.toFixed(1)}時間</td>
                    <td>${coreTime1}</td>
                    <td>${coreTime2}</td>
                    <td class="${violationClass}">${violationText}</td>
                `;
                studentList.appendChild(row);
            } catch (error) {
                console.error(`学生 ${student.student_id} のデータ取得に失敗:`, error);
                // エラーが発生しても他の学生のデータは表示を続ける
                continue;
            }
        }
    } catch (error) {
        console.error('データの取得に失敗しました:', error);
        const studentList = document.getElementById('studentList');
        studentList.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    データの取得に失敗しました。<br>
                    エラー: ${error.message}<br>
                    <button class="btn btn-outline-danger mt-2" onclick="loadStudentData()">再読み込み</button>
                </td>
            </tr>
        `;
    }
}

// コアタイムの表示形式を整形する関数
function formatCoreTime(day, period) {
    if (!day || !period) return '-';
    return `${DAYS_OF_WEEK[day]}曜${PERIODS[period]}`;
}

// コアタイムチェックの実行
async function checkCoreTime(period) {
    try {
        const response = await fetch(`${API_BASE_URL}/core-time/check/${period}`);
        if (!response.ok) {
            throw new Error(`コアタイムチェックに失敗: ${response.status}`);
        }
        const result = await response.json();
        
        // 更新された学生データを反映
        if (result.updated_students) {
            const studentList = document.getElementById('studentList');
            const rows = studentList.getElementsByTagName('tr');
            
            for (const updatedStudent of result.updated_students) {
                for (const row of rows) {
                    const studentIdCell = row.cells[0];
                    if (studentIdCell && studentIdCell.textContent === updatedStudent.student_id) {
                        const violationCell = row.cells[6];
                        if (violationCell) {
                            const violationClass = updatedStudent.core_time_violations > 0 ? 'violation' : '';
                            const violationText = updatedStudent.core_time_violations > 0 ? 
                                `<span class="text-danger fw-bold">${updatedStudent.core_time_violations}回</span>` : 
                                '<span class="text-muted">0回</span>';
                            violationCell.className = violationClass;
                            violationCell.innerHTML = violationText;
                        }
                        break;
                    }
                }
            }
        }
        
        return result;
    } catch (error) {
        console.error('コアタイムチェックに失敗しました:', error);
        throw error;
    }
} 