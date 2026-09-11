// 현재 보고 있는 영상 상태 (초기 null)
    let currentVideo = null;
    let chatHistory = [];

    document.addEventListener("DOMContentLoaded", () => {
      const savedKey = localStorage.getItem("GEMINI_API_KEY");
      if (savedKey) {
        document.getElementById("api-key-input").value = savedKey;
      }
    });

    function toggleApiKeyModal() {
      const modal = document.getElementById("api-modal");
      modal.classList.toggle("hidden");
    }

    function saveApiKey() {
      const key = document.getElementById("api-key-input").value.trim();
      if (key) {
        localStorage.setItem("GEMINI_API_KEY", key);
      } else {
        localStorage.removeItem("GEMINI_API_KEY");
      }
      toggleApiKeyModal();
      alert("API 키가 저장되었습니다.");
    }

    // ======================================================================
    // 🕒 최근 검색/시청 기록 (Watch History) & 타임스탬프 캐시 로컬스토리지 관리
    // ======================================================================
    const HISTORY_STORAGE_KEY = "HYDOK_WATCH_HISTORY";
    const TIMESTAMPS_STORAGE_KEY = "HYDOK_TIMESTAMPS_CACHE";

    function getWatchHistory() {
      try {
        const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
      } catch (e) {
        return [];
      }
    }

    // 영상별 저장된 타임스탬프 불러오기
    function getStoredTimestamps(videoId) {
      if (!videoId) return null;
      try {
        const raw = localStorage.getItem(TIMESTAMPS_STORAGE_KEY);
        if (raw) {
          const cache = JSON.parse(raw);
          if (cache && cache[videoId] && cache[videoId].length > 0) {
            return cache[videoId];
          }
        }
        // 시청 기록 객체에서도 검색
        const history = getWatchHistory();
        const found = history.find(item => item.id === videoId);
        if (found && found.timestamps && found.timestamps.length > 0) {
          return found.timestamps;
        }
      } catch (e) {}
      return null;
    }

    // 영상별 타임스탬프 로컬 저장
    function saveStoredTimestamps(videoId, timestamps) {
      if (!videoId || !timestamps || timestamps.length === 0) return;
      try {
        // 1. 타임스탬프 캐시 저장
        const raw = localStorage.getItem(TIMESTAMPS_STORAGE_KEY);
        const cache = raw ? JSON.parse(raw) : {};
        cache[videoId] = timestamps;
        localStorage.setItem(TIMESTAMPS_STORAGE_KEY, JSON.stringify(cache));

        // 2. 시청 기록 목록에도 타임스탬프 동기화
        let history = getWatchHistory();
        let updated = false;
        history = history.map(item => {
          if (item.id === videoId) {
            item.timestamps = timestamps;
            updated = true;
          }
          return item;
        });
        if (updated) {
          localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
          renderWatchHistory();
        }
      } catch (e) {}
    }

    function saveWatchHistory(videoData, rawUrl, timestamps) {
      if (!videoData || !videoData.id) return;
      let history = getWatchHistory();
      
      // 기존 동일 영상 id 제거 (최신 위치로 올리기 위함)
      const existing = history.find(item => item.id === videoData.id);
      const effectiveTimestamps = timestamps || (videoData.timestamps && videoData.timestamps.length > 0 ? videoData.timestamps : (existing ? existing.timestamps : null));

      history = history.filter(item => item.id !== videoData.id);

      const newItem = {
        id: videoData.id,
        title: videoData.title || "제목 없음",
        uploader: videoData.uploader || "채널",
        thumbnail: videoData.thumbnail || `https://i.ytimg.com/vi/${videoData.id}/hqdefault.jpg`,
        url: rawUrl || `https://www.youtube.com/watch?v=${videoData.id}`,
        duration_min_str: videoData.duration_min_str || "",
        timestamps: effectiveTimestamps || [],
        timestamp: Date.now()
      };

      // 최신 항목을 가장 앞에 추가
      history.unshift(newItem);

      // 최대 8개까지 유지
      if (history.length > 8) {
        history = history.slice(0, 8);
      }

      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
      renderWatchHistory();
    }

    function deleteHistoryItem(id) {
      let history = getWatchHistory();
      history = history.filter(item => item.id !== id);
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
      
      // 캐시에서도 삭제
      try {
        const raw = localStorage.getItem(TIMESTAMPS_STORAGE_KEY);
        if (raw) {
          const cache = JSON.parse(raw);
          delete cache[id];
          localStorage.setItem(TIMESTAMPS_STORAGE_KEY, JSON.stringify(cache));
        }
      } catch (e) {}

      renderWatchHistory();
    }

    function clearAllHistory() {
      if (confirm("최근 시청 기록과 저장된 타임스탬프를 모두 삭제하시겠습니까?")) {
        localStorage.removeItem(HISTORY_STORAGE_KEY);
        localStorage.removeItem(TIMESTAMPS_STORAGE_KEY);
        renderWatchHistory();
      }
    }

    function renderWatchHistory() {
      const section = document.getElementById("history-section");
      const listEl = document.getElementById("history-list");
      const badge = document.getElementById("history-count-badge");
      if (!section || !listEl) return;

      const history = getWatchHistory();

      if (history.length === 0) {
        section.classList.add("hidden");
        listEl.innerHTML = "";
        return;
      }

      section.classList.remove("hidden");
      if (badge) badge.innerText = history.length;

      let html = "";
      history.forEach(item => {
        const safeTitle = (item.title || "").replace(/"/g, '&quot;');
        const safeUrl = (item.url || `https://www.youtube.com/watch?v=${item.id}`).replace(/"/g, '&quot;');
        const safeUploader = (item.uploader || "").replace(/"/g, '&quot;');
        const thumb = item.thumbnail || `https://i.ytimg.com/vi/${item.id}/hqdefault.jpg`;
        const duration = item.duration_min_str ? `<span class="absolute bottom-0.5 right-0.5 bg-black/80 text-white text-[9px] px-1 rounded font-mono">${item.duration_min_str}</span>` : '';
        
        // 타임스탬프 저장 여부 뱃지
        const tsList = item.timestamps && item.timestamps.length > 0 ? item.timestamps : getStoredTimestamps(item.id);
        const tsBadge = (tsList && tsList.length > 0) 
          ? `<span class="inline-flex items-center gap-0.5 text-[9px] text-[#923826] bg-[#f5ebe6] px-1.5 py-0.2 rounded font-medium ml-1.5">⏱️ ${tsList.length}개 챕터</span>`
          : '';

        html += `
          <div class="group relative bg-white hover:bg-[#ede8df] border border-[#e2dcd1] hover:border-[#b8b0a2] rounded-xl p-2.5 transition flex items-center justify-between space-x-2.5 shadow-2xs text-left">
            <div class="flex items-center space-x-2.5 flex-1 min-w-0 cursor-pointer" onclick="loadVideoFromUrl('${safeUrl}')" title="${safeTitle}">
              <div class="relative w-16 h-10 rounded-md overflow-hidden bg-[#1c1917] shrink-0 border border-[#e2dcd1]">
                <img src="${thumb}" alt="" class="w-full h-full object-cover group-hover:scale-105 transition" onerror="this.src='https://i.ytimg.com/vi/${item.id}/hqdefault.jpg'" />
                ${duration}
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-xs font-bold text-[#1c1917] group-hover:text-[#923826] truncate leading-tight transition">
                  ${safeTitle}
                </div>
                <div class="text-[11px] text-[#8a8376] truncate mt-0.5 flex items-center">
                  <span class="truncate">${safeUploader}</span>
                  ${tsBadge}
                </div>
              </div>
            </div>
            <button 
              onclick="event.stopPropagation(); deleteHistoryItem('${item.id}')" 
              class="w-6 h-6 rounded-full hover:bg-[#ded7ca] text-[#b0a99c] hover:text-[#923826] flex items-center justify-center text-xs transition shrink-0 cursor-pointer" 
              title="이 기록 삭제"
            >
              ✕
            </button>
          </div>
        `;
      });
      listEl.innerHTML = html;
    }

    // 🎯 랜딩 페이지에서 시작 버튼 클릭
    function startFromLanding() {
      const input = document.getElementById("landing-url-input");
      const url = input.value.trim();
      if (!url) {
        alert("유튜브 동영상 주소(URL)를 입력해 주세요.");
        input.focus();
        return;
      }
      loadVideoFromUrl(url);
    }

    // 🚀 글로벌 프로그레스 컨트롤러 (Progress Controller)
    const ProgressController = {
      timer: null,
      currentProgress: 0,

      // 프로그레스 시작 (showOverlay=true 시 화면 중앙 인디케이터 모달도 함께 표시)
      start(title = "영상 분석 및 큐레이션 중", subtitle = "유튜브 스트림 및 자막 데이터를 수집하고 있습니다...", showOverlay = true) {
        clearInterval(this.timer);
        this.currentProgress = 12;

        // 1. 최상단 슬릭 프로그레스 바 활성화
        const topContainer = document.getElementById("top-progress-container");
        const topBar = document.getElementById("top-progress-bar");
        if (topContainer && topBar) {
          topBar.style.width = "12%";
          topContainer.classList.remove("opacity-0");
          topContainer.classList.add("opacity-100");
        }

        // 2. 중앙 오버레이 모달 활성화
        if (showOverlay) {
          const overlay = document.getElementById("loading-overlay");
          const card = document.getElementById("loading-modal-card");
          const titleEl = document.getElementById("loading-title");
          const subEl = document.getElementById("loading-subtitle");
          const stepEl = document.getElementById("loading-step-text");
          const pctEl = document.getElementById("loading-percentage");
          const innerBar = document.getElementById("loading-inner-bar");

          if (titleEl) titleEl.innerText = title;
          if (subEl) subEl.innerText = subtitle;
          if (stepEl) stepEl.innerText = "유튜브 메타데이터 수집 중...";
          if (pctEl) pctEl.innerText = "12%";
          if (innerBar) innerBar.style.width = "12%";

          if (overlay) {
            overlay.classList.remove("opacity-0", "pointer-events-none");
            overlay.classList.add("opacity-100");
          }
          if (card) {
            card.classList.remove("scale-95");
            card.classList.add("scale-100");
          }
        }

        // 3. 점진적 진행률 시뮬레이션
        const milestones = [
          { threshold: 38, text: "유튜브 스트림 정보 및 채널 확인 중..." },
          { threshold: 65, text: "자막 및 타임스탬프 챕터 구조 분석 중..." },
          { threshold: 88, text: "AI 저널 및 대화 세션 준비 중..." },
          { threshold: 94, text: "화면 레이아웃 렌더링 단계..." }
        ];
        let mIdx = 0;

        this.timer = setInterval(() => {
          if (mIdx < milestones.length) {
            const m = milestones[mIdx];
            if (this.currentProgress < m.threshold) {
              this.currentProgress += Math.floor(Math.random() * 4) + 2;
              if (this.currentProgress > m.threshold) this.currentProgress = m.threshold;
              this.update(this.currentProgress, m.text);
            } else {
              mIdx++;
            }
          }
        }, 110);
      },

      // 진행률 업데이트
      update(percent, text) {
        const topBar = document.getElementById("top-progress-bar");
        if (topBar) topBar.style.width = `${percent}%`;

        const pctEl = document.getElementById("loading-percentage");
        const innerBar = document.getElementById("loading-inner-bar");
        const stepEl = document.getElementById("loading-step-text");

        if (pctEl) pctEl.innerText = `${percent}%`;
        if (innerBar) innerBar.style.width = `${percent}%`;
        if (text && stepEl) stepEl.innerText = text;
      },

      // 프로그레스 완료
      finish(isSuccess = true) {
        clearInterval(this.timer);
        this.update(100, isSuccess ? "준비가 완료되었습니다!" : "요청이 완료되었습니다.");

        setTimeout(() => {
          // 탑 프로그레스 바 페이드아웃
          const topContainer = document.getElementById("top-progress-container");
          const topBar = document.getElementById("top-progress-bar");
          if (topContainer) {
            topContainer.classList.remove("opacity-100");
            topContainer.classList.add("opacity-0");
            setTimeout(() => { if (topBar) topBar.style.width = "0%"; }, 300);
          }

          // 중앙 오버레이 모달 페이드아웃
          const overlay = document.getElementById("loading-overlay");
          const card = document.getElementById("loading-modal-card");
          if (card) {
            card.classList.remove("scale-100");
            card.classList.add("scale-95");
          }
          if (overlay) {
            overlay.classList.remove("opacity-100");
            overlay.classList.add("opacity-0", "pointer-events-none");
          }
        }, 350);
      }
    };

    // 🧠 영상 데이터 및 AI 대화 인메모리 캐시 저장소 (Instant Restore Cache)
    const videoDataCache = new Map(); // key: videoId 또는 url -> value: videoData
    const videoChatCache = new Map(); // key: videoId -> value: { history: [...], domHtml: '...' }

    // 영상 ID 추출 헬퍼 (다양한 유튜브 URL 형식 지원)
    function extractVideoId(url) {
      if (!url) return null;
      url = url.trim();
      if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
      const m1 = url.match(/(?:youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]{11})/);
      if (m1) return m1[1];
      const m2 = url.match(/[?&]v=([^#&?]{11})/);
      if (m2) return m2[1];
      return null;
    }

    // 영상 전환 전 현재 보고 있던 영상의 AI 대화 상태 저장
    function saveCurrentChatState() {
      if (currentVideo && currentVideo.id) {
        const chatListEl = document.getElementById("dynamic-chat-list");
        videoChatCache.set(currentVideo.id, {
          history: [...chatHistory],
          domHtml: chatListEl ? chatListEl.innerHTML : ""
        });
      }
    }

    // 화면에 영상 메타데이터와 UI를 즉시 적용하는 렌더러
    function renderVideoWorkspace(data, url, pushHistory = true) {
      currentVideo = data;

      // 1. 브라우저 히스토리 동기화 (뒤로가기/앞으로가기)
      if (pushHistory) {
        const pageUrl = `?v=${data.id}`;
        window.history.pushState({ view: "workspace", url: url, videoId: data.id }, "", pageUrl);
      }

      // 2. 최근 시청 기록에 저장
      saveWatchHistory(data, url);

      // 3. 랜딩 페이지 숨기고 2컬럼 워크스페이스 표시!
      document.getElementById("landing-view").classList.add("hidden");
      document.getElementById("workspace-view").classList.remove("hidden");

      // 4. URL 입력창 동기화
      const topInput = document.getElementById("top-url-input");
      const landingInput = document.getElementById("landing-url-input");
      if (topInput) topInput.value = url;
      if (landingInput) landingInput.value = url;

      // 5. YouTube IFrame 플레이어 교체 & 즉시 재생 (iframe 서브프레임 히스토리 오염 방지)
      const oldIframe = document.getElementById("youtube-player");
      if (oldIframe) {
        const newIframe = oldIframe.cloneNode(false);
        newIframe.src = `https://www.youtube.com/embed/${data.id}?autoplay=1&enablejsapi=1&rel=0`;
        oldIframe.parentNode.replaceChild(newIframe, oldIframe);
      }

      // 6. 좌측 영상 메타 정보 갱신
      document.getElementById("video-category-tag").innerText = `${data.category || 'JOURNAL'} • ${data.duration_min_str || '영상'}`;
      document.getElementById("video-title").innerText = data.title;
      document.getElementById("video-meta-sub").innerHTML = `<span>${data.view_count_str}</span><span>•</span><span>${data.upload_date_str}</span>`;
      document.getElementById("channel-avatar").innerText = data.avatar_letter || "R";
      document.getElementById("channel-name").innerText = data.uploader;
      document.getElementById("channel-subscribers").innerText = data.subscribers_str;
      document.getElementById("btn-like-count").innerText = data.like_count_str || "추천";
      document.getElementById("video-description").innerText = data.description || "영상 설명이 없습니다.";

      // 7. 우측 AI 챗봇 복원 (이전 대화가 캐시되어 있으면 그대로 복원, 없으면 초기화)
      const cachedChat = videoChatCache.get(data.id);
      const chatListEl = document.getElementById("dynamic-chat-list");
      const chatInput = document.getElementById("chat-user-input");
      if (chatInput) chatInput.placeholder = "영상에 대해 질문해 보세요";

      if (cachedChat && cachedChat.history && cachedChat.history.length > 0) {
        chatHistory = [...cachedChat.history];
        if (chatListEl) chatListEl.innerHTML = cachedChat.domHtml || "";
      } else {
        chatHistory = [];
        if (chatListEl) chatListEl.innerHTML = "";
        document.getElementById("welcome-text").innerHTML = `안녕하세요. 지금 보고 계신 『${data.title}』의 자막과 내용을 분석했습니다. 요약, 특정 장면 찾기, 용어 설명 모두 편하게 물어보세요!`;
      }

      // 8. 타임스탬프 로드 (우선순위: 유튜브 자체 메타 -> 로컬스토리지 캐시 -> 샘플 -> AI 자동생성)
      const storedTs = getStoredTimestamps(data.id);
      if (data.timestamps && data.timestamps.length > 0) {
        saveStoredTimestamps(data.id, data.timestamps);
        renderTimestamps(data.timestamps);
      } else if (storedTs && storedTs.length > 0) {
        renderTimestamps(storedTs);
      } else if (SAMPLE_TIMESTAMPS[data.id]) {
        saveStoredTimestamps(data.id, SAMPLE_TIMESTAMPS[data.id]);
        renderTimestamps(SAMPLE_TIMESTAMPS[data.id]);
      } else {
        refreshAiTimestamps();
      }
    }

    // 유튜브 URL로부터 영상 및 메타데이터 로드 (캐시 우선 검사)
    async function loadVideoFromUrl(explicitUrl, pushHistory = true) {
      const topInput = document.getElementById("top-url-input");
      const landingInput = document.getElementById("landing-url-input");
      const landingBtn = document.getElementById("btn-landing-start");
      const topBtn = document.getElementById("btn-top-search");

      const url = explicitUrl || (topInput ? topInput.value.trim() : "") || (landingInput ? landingInput.value.trim() : "");
      if (!url) {
        alert("유튜브 동영상 링크(URL)를 입력해 주세요.");
        return;
      }

      // 현재 보고 있던 영상의 AI 대화 상태 캐시 백업
      saveCurrentChatState();

      // ⚡ [캐시 우선 확인] 이미 조회했던 데이터가 있으면 로딩 프로그레스 없이 0초 즉시 복원!
      const vid = extractVideoId(url);
      const cachedData = (vid && videoDataCache.get(vid)) || videoDataCache.get(url);

      if (cachedData) {
        renderVideoWorkspace(cachedData, url, pushHistory);
        return;
      }

      // 처음 조회하는 영상인 경우에만 로딩 프로그레스 가동
      ProgressController.start("영상 분석 및 큐레이션 중", "유튜브 스트림 및 자막 데이터를 수집하고 있습니다...", true);

      if (landingBtn) {
        landingBtn.innerHTML = `<span>분석 중...</span><span class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>`;
        landingBtn.disabled = true;
      }
      if (topBtn) {
        topBtn.innerHTML = `<span class="w-3.5 h-3.5 border-2 border-[#923826] border-t-transparent rounded-full animate-spin"></span>`;
        topBtn.disabled = true;
      }

      try {
        const res = await fetch("/api/video-info", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: url })
        });
        const resData = await res.json();
        if (!res.ok) {
          throw new Error(resData.detail || "영상 정보를 가져올 수 없습니다.");
        }

        const data = resData.data;

        // 캐시에 저장하여 뒤로가기/앞으로가기 시 즉시 표시
        videoDataCache.set(url, data);
        if (data.id) videoDataCache.set(data.id, data);

        // UI 렌더링
        renderVideoWorkspace(data, url, pushHistory);

        // 프로그레스 정상 완료
        ProgressController.finish(true);

      } catch (err) {
        ProgressController.finish(false);
        alert("영상 로드 오류: " + err.message);
      } finally {
        if (landingBtn) {
          landingBtn.innerHTML = `<span>시작하기</span><span>→</span>`;
          landingBtn.disabled = false;
        }
        if (topBtn) {
          topBtn.innerHTML = `<span>재생 ↵</span>`;
          topBtn.disabled = false;
        }
      }
    }

    // 초기 랜딩 페이지(URL만 입력받는 화면)로 리셋
    function resetToLanding(pushHistory = true) {
      saveCurrentChatState();

      const oldIframe = document.getElementById("youtube-player");
      if (oldIframe) {
        const newIframe = oldIframe.cloneNode(false);
        newIframe.src = "";
        oldIframe.parentNode.replaceChild(newIframe, oldIframe);
      }
      currentVideo = null;

      if (pushHistory) {
        window.history.pushState({ view: "landing" }, "", window.location.pathname);
      }

      // 뷰 전환: 워크스페이스 숨기고 랜딩 표시
      document.getElementById("workspace-view").classList.add("hidden");
      document.getElementById("landing-view").classList.remove("hidden");

      // 입력창 초기화 및 포커스
      document.getElementById("top-url-input").value = "";
      const landingInput = document.getElementById("landing-url-input");
      landingInput.value = "";
      setTimeout(() => landingInput.focus(), 100);

      // 시청 기록 최신 렌더링
      renderWatchHistory();

      // 챗 및 타임스탬프 상태 초기화
      chatHistory = [];
      document.getElementById("dynamic-chat-list").innerHTML = "";
      renderTimestamps([]);
      switchRightTab("chat");
    }

    // 이전 호환성을 위한 alias
    function resetToEmptyState() {
      resetToLanding();
    }
    function loadSampleVideo(url) {
      loadVideoFromUrl(url);
    }

    // 추천 칩 클릭 시 즉각 질문 전송
    function sendQuickChip(questionText) {
      if (!currentVideo) {
        alert("먼저 상단에 유튜브 링크를 입력하거나 좌측의 샘플 영상을 선택해 주세요.");
        return;
      }
      document.getElementById("chat-user-input").value = questionText;
      sendChatMessage();
    }

    // 🔔 글로벌 토스트 알림 함수
    function showToast(message, isSuccess = true) {
      const toast = document.getElementById("hydok-toast");
      const msgEl = document.getElementById("hydok-toast-msg");
      const iconEl = document.getElementById("hydok-toast-icon");
      if (!toast || !msgEl) return;

      msgEl.innerText = message;
      if (iconEl) {
        iconEl.innerText = isSuccess ? "✓" : "⚠️";
        iconEl.className = isSuccess ? "text-[#34a853] font-bold" : "text-amber-400 font-bold";
      }
      toast.classList.remove("opacity-0", "pointer-events-none", "-translate-y-2");
      toast.classList.add("opacity-100", "translate-y-0");

      clearTimeout(window._toastTimer);
      window._toastTimer = setTimeout(() => {
        toast.classList.remove("opacity-100", "translate-y-0");
        toast.classList.add("opacity-0", "pointer-events-none", "-translate-y-2");
      }, 3000);
    }

    // 📋 100% 보장 클립보드 복사 함수 (Clipboard API + Fallback)
    async function copyToClipboard(text) {
      if (!text) return false;
      // 1. Modern Clipboard API
      if (navigator.clipboard && window.isSecureContext) {
        try {
          await navigator.clipboard.writeText(text);
          return true;
        } catch (err) {
          console.warn("Clipboard API failed, fallback to execCommand:", err);
        }
      }
      // 2. Fallback execCommand
      try {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        textArea.style.top = "-9999px";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const success = document.execCommand("copy");
        document.body.removeChild(textArea);
        return success;
      } catch (err) {
        console.error("Fallback copy failed:", err);
        return false;
      }
    }

    // 📋 실제 유튜브 영상의 직통 URL(watch?v=...)을 실시간 조회하여 클립보드에 복사
    async function copyVideoUrl(queryOrUrl, btn) {
      if (!queryOrUrl) return;

      const originalHtml = btn ? btn.innerHTML : "";
      if (btn) {
        btn.innerHTML = `<span class="inline-block w-3 h-3 border-2 border-[#923826] border-t-transparent rounded-full animate-spin"></span><span class="text-[10px] ml-1">주소 찾는 중...</span>`;
        btn.disabled = true;
      }

      try {
        let finalUrl = queryOrUrl.trim();

        // 만약 이미 watch?v= 나 youtu.be/ 형태의 11자리 비디오 링크라면 그대로 사용
        const isDirect = (finalUrl.includes("youtube.com/watch?v=") || finalUrl.includes("youtu.be/")) && !finalUrl.includes("search_query");
        if (!isDirect) {
          const res = await fetch("/api/resolve-video-url", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query_or_url: finalUrl })
          });
          const resData = await res.json();
          if (res.ok && resData.url) {
            finalUrl = resData.url;
          } else {
            throw new Error(resData.detail || "실제 영상을 조회하지 못했습니다.");
          }
        }

        // 클립보드 복사 실행
        const success = await copyToClipboard(finalUrl);
        if (!success) {
          prompt("아래 직통 링크를 복사하세요:", finalUrl);
        } else {
          showToast(`📋 유튜브 주소 복사 완료!\n${finalUrl}`, true);
        }

        if (btn) {
          btn.innerHTML = `<span>✓ 직통 링크 복사완료!</span>`;
          btn.classList.add("bg-[#e6f4ea]", "border-[#34a853]", "text-[#137333]");
          setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.classList.remove("bg-[#e6f4ea]", "border-[#34a853]", "text-[#137333]");
            btn.disabled = false;
          }, 2500);
        }
      } catch (e) {
        if (btn) {
          btn.innerHTML = `<span>⚠️ 복사 실패</span>`;
          setTimeout(() => {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
          }, 2000);
        }
        showToast("영상 직통 링크를 가져오지 못했습니다: " + e.message, false);
      }
    }

    // 💬 AI 말풍선 DOM 생성 및 [링크복사] 버튼 완전 바인딩
    function appendAiBubble(replyText, dynamicList) {
      if (!replyText) return;

      // 1. 마크다운 텍스트 전처리: [링크복사](키워드) 또는 📋 링크복사 마커 변환
      let processed = replyText;

      // 1-1. 마크다운 링크 [링크복사](키워드) -> 마커 span
      processed = processed.replace(/\[링크복사\]\(([^)]+)\)/gi, (m, query) => {
        return `<span class="copy-url-marker" data-query="${encodeURIComponent(query.trim())}"></span>`;
      });

      // 1-2. 텍스트 형태 (📋 링크복사 또는 [링크복사]) -> 마커 span
      processed = processed.replace(/(?:📋\s*)?\[?링크\s*복사\]?(?!\()/gi, `<span class="copy-url-marker" data-query=""></span>`);

      // 2. marked 파싱
      let html = marked.parse(processed);

      // 3. 말풍선 엘리먼트 생성
      const aiBubble = document.createElement("div");
      aiBubble.className = "space-y-1.5";
      aiBubble.innerHTML = `
        <div class="text-[10px] font-bold text-[#9e9688] uppercase tracking-wider">HYDOK AI</div>
        <div class="ai-chat-content bg-white rounded-2xl rounded-tl-sm p-3.5 shadow-sm border border-[#e5dfd4] text-xs text-[#2b2724] leading-relaxed chat-prose">
          ${html}
        </div>
      `;

      const contentBox = aiBubble.querySelector(".ai-chat-content");

      // 4. copy-url-marker 요소들을 인터랙티브 버튼으로 교체 및 이벤트 바인딩
      const markers = contentBox.querySelectorAll(".copy-url-marker");
      markers.forEach(marker => {
        let query = decodeURIComponent(marker.dataset.query || "");

        // 쿼리가 비어있는 경우 앞선 텍스트나 문맥에서 영상 제목/채널명 자동 추론
        if (!query) {
          let prev = marker.parentElement;
          while (prev && prev !== contentBox) {
            const text = prev.innerText || "";
            const lines = text.split("\n").map(l => l.trim()).filter(Boolean);
            if (lines.length > 0) {
              query = lines[0].replace(/^[0-9]+[\.\)]\s*/, "").replace(/[📋\[\]]/g, "").trim();
              break;
            }
            prev = prev.previousElementSibling || prev.parentElement;
          }
        }

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "inline-flex items-center gap-1.5 px-3 py-1 my-1.5 bg-[#ede8df] hover:bg-[#ded7ca] active:scale-95 border border-[#cfc8bc] text-[#4a453d] text-[11px] font-semibold rounded-full shadow-2xs transition cursor-pointer select-none";
        btn.innerHTML = `<span>📋 직통 링크복사</span>`;
        
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          copyVideoUrl(query || currentVideo?.title || "", btn);
        });

        marker.parentNode.replaceChild(btn, marker);
      });

      // 5. 일반 a 태그 중 남아있는 유튜브 링크 등도 버튼으로 변환
      const links = contentBox.querySelectorAll("a");
      links.forEach(a => {
        const href = a.getAttribute("href") || "";
        const text = a.innerText.trim();

        if (text.includes("링크복사") || text.includes("링크 복사") || href.includes("youtube.com") || href.includes("youtu.be")) {
          const target = href.replace(/^search:/, "").trim() || text;
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "inline-flex items-center gap-1.5 px-3 py-1 my-1.5 bg-[#ede8df] hover:bg-[#ded7ca] active:scale-95 border border-[#cfc8bc] text-[#4a453d] text-[11px] font-semibold rounded-full shadow-2xs transition cursor-pointer select-none";
          btn.innerHTML = `<span>📋 직통 링크복사</span>`;
          btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            copyVideoUrl(target, btn);
          });
          a.parentNode.replaceChild(btn, a);
        } else {
          a.setAttribute("target", "_blank");
          a.setAttribute("rel", "noopener noreferrer");
          a.className = "text-[#923826] underline hover:text-[#1c1917] font-semibold";
        }
      });

      dynamicList.appendChild(aiBubble);
    }

    // 💬 한글(IME) 조합 상태 및 중복 전송 방지 플래그
    let isChatComposing = false;
    let isSendingChat = false;

    // 한글 입력 중 엔터 키 처리 (IME 조합 중복 전송 방지)
    function handleChatInputKeyDown(e) {
      if (e.key === "Enter" && !e.shiftKey) {
        // 한글 조합 중이거나 keyCode가 229인 경우 엔터는 조합 확정만 하고 메시지 전송은 차단
        if (e.isComposing || isChatComposing || e.keyCode === 229) {
          return;
        }
        e.preventDefault();
        sendChatMessage();
      }
    }

    // AI 대화 메시지 전송
    async function sendChatMessage() {
      if (isSendingChat) return;

      if (!currentVideo) {
        alert("먼저 상단에 유튜브 링크를 입력하거나 좌측의 샘플 영상을 선택해 주세요.");
        return;
      }

      const input = document.getElementById("chat-user-input");
      const msg = input.value.trim();
      if (!msg) return;

      isSendingChat = true;

      const apiKey = localStorage.getItem("GEMINI_API_KEY") || "";
      const chatContainer = document.getElementById("chat-messages-container");
      const dynamicList = document.getElementById("dynamic-chat-list");
      const loadingEl = document.getElementById("chat-loading");
      const sendBtn = document.getElementById("send-msg-btn");

      // 1. 유저 말풍선 렌더링
      const userBubble = document.createElement("div");
      userBubble.className = "flex justify-end";
      userBubble.innerHTML = `
        <div class="bg-[#1c1917] text-white rounded-2xl rounded-tr-sm p-3 text-xs leading-relaxed max-w-[85%] shadow-sm">
          ${msg}
        </div>
      `;
      dynamicList.appendChild(userBubble);

      // 입력창 즉시 초기화
      input.value = "";
      chatContainer.scrollTop = chatContainer.scrollHeight;

      // 브라우저 IME의 조합 잔여 글자(마지막 글자 1타) 강제 청소
      setTimeout(() => {
        if (input.value && (msg.endsWith(input.value) || input.value === msg.slice(-1))) {
          input.value = "";
        }
      }, 0);
      setTimeout(() => {
        if (input.value && (msg.endsWith(input.value) || input.value === msg.slice(-1))) {
          input.value = "";
        }
      }, 40);

      // 2. 로딩 표시 활성화
      loadingEl.classList.remove("hidden");
      sendBtn.disabled = true;

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            video_info: currentVideo,
            message: msg,
            chat_history: chatHistory,
            api_key: apiKey
          })
        });

        const resData = await response.json();
        if (!response.ok) {
          throw new Error(resData.detail || "답변을 불러오지 못했습니다.");
        }

        const replyText = resData.reply;

        // 히스토리 누적
        chatHistory.push({ role: "user", text: msg });
        chatHistory.push({ role: "model", text: replyText });

        // 3. AI 말풍선 렌더링 (원클릭 직통 링크복사 버튼 자동 바인딩)
        appendAiBubble(replyText, dynamicList);

      } catch (err) {
        const errorBubble = document.createElement("div");
        errorBubble.className = "space-y-1.5";
        errorBubble.innerHTML = `
          <div class="text-[10px] font-bold text-red-500 uppercase tracking-wider">HYDOK AI 오류</div>
          <div class="bg-red-50 text-red-800 rounded-2xl rounded-tl-sm p-3 text-xs border border-red-200">
            ⚠️ ${err.message}
          </div>
        `;
        dynamicList.appendChild(errorBubble);
      } finally {
        loadingEl.classList.add("hidden");
        sendBtn.disabled = false;
        isSendingChat = false;
        input.value = "";
        chatContainer.scrollTop = chatContainer.scrollHeight;
        setTimeout(() => input.focus(), 50);
      }
    }

    // 타임스탬프 전역 상태
    let currentTimestamps = [];

    // 추천 샘플 영상별 기본 타임스탬프 데이터
    const SAMPLE_TIMESTAMPS = {
      "PjPqf60C8h8": [
        { seconds: 0, time_str: "00:00", title: "도입부: 서울 을지로의 마지막 활판 인쇄소" },
        { seconds: 85, time_str: "01:25", title: "주조기: 300도 뜨거운 납을 녹여 글자를 만드는 순간" },
        { seconds: 240, time_str: "04:00", title: "문선(文選): 수만 개 활자 상자에서 글자 하나를 찾는 손길" },
        { seconds: 435, time_str: "07:15", title: "인쇄기의 육중한 숨소리와 종이에 새겨지는 압력" },
        { seconds: 610, time_str: "10:10", title: "장인 인터뷰: 기계가 사라져도 손의 감각은 영원하다" }
      ],
      "j9eYmC2Nl9E": [
        { seconds: 0, time_str: "00:00", title: "Google Gemini 1.5 & 차세대 모델 공개" },
        { seconds: 48, time_str: "00:48", title: "백만 토큰 컨텍스트 윈도우의 혁신" },
        { seconds: 125, time_str: "02:05", title: "비디오 및 오디오 멀티모달 실시간 추론 시연" },
        { seconds: 215, time_str: "03:35", title: "개발자와 크리에이터를 위한 새로운 가능성" }
      ],
      "2pmPqyJ_w_w": [
        { seconds: 0, time_str: "00:00", title: "오프닝 및 아티스트 Lewis Capaldi 소개" },
        { seconds: 52, time_str: "00:52", title: "글래스톤베리 무대와 감동적인 비하인드 스토리" },
        { seconds: 155, time_str: "02:35", title: "솔직한 인터뷰: 음악이 삶을 구원하는 순간들" },
        { seconds: 245, time_str: "04:05", title: "라이브 퍼포먼스 하이라이트" }
      ]
    };

    // 💡 타임스탬프 화면 렌더링
    function renderTimestamps(list) {
      currentTimestamps = list || [];
      const emptyEl = document.getElementById("ts-empty-state");
      const listEl = document.getElementById("ts-items-list");
      const badgeCount = document.getElementById("ts-badge-count");

      if (!list || list.length === 0) {
        emptyEl.classList.remove("hidden");
        listEl.innerHTML = "";
        badgeCount.classList.add("hidden");
        return;
      }

      emptyEl.classList.add("hidden");
      badgeCount.innerText = list.length;
      badgeCount.classList.remove("hidden");

      let html = "";
      list.forEach((item, idx) => {
        html += `
          <button 
            onclick="seekToTimestamp(${item.seconds}, this)" 
            class="timestamp-card w-full text-left p-3 rounded-xl bg-white hover:bg-[#ede8df] border border-[#e5dfd4] transition flex items-center justify-between group shadow-2xs cursor-pointer"
          >
            <div class="flex items-center space-x-3 min-w-0 flex-1">
              <span class="ts-badge px-2.5 py-1 rounded-md bg-[#eeeae1] group-hover:bg-[#1c1917] group-hover:text-white text-[#923826] font-mono text-xs font-bold transition shrink-0">
                ${item.time_str}
              </span>
              <span class="text-xs font-medium text-[#2b2724] group-hover:text-[#1c1917] truncate leading-tight">
                ${item.title}
              </span>
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 ml-2">
              <span class="text-[10px] text-[#8a8376] hidden group-hover:inline">재생</span>
              <span class="text-xs text-[#b0a99c] group-hover:text-[#923826] transition">▶</span>
            </div>
          </button>
        `;
      });
      listEl.innerHTML = html;
    }

    // 🎯 타임스탬프 클릭 시 유튜브 영상 해당 위치로 즉시 이동
    function seekToTimestamp(seconds, el) {
      const iframe = document.getElementById("youtube-player");
      if (!iframe || !iframe.contentWindow) return;

      // 1. YouTube IFrame API 메시지 전송 (Seek & Play)
      iframe.contentWindow.postMessage(JSON.stringify({
        event: "command",
        func: "seekTo",
        args: [seconds, true]
      }), "*");

      iframe.contentWindow.postMessage(JSON.stringify({
        event: "command",
        func: "playVideo",
        args: []
      }), "*");

      // 2. 선택된 항목 하이라이트 스타일 적용
      document.querySelectorAll(".timestamp-card").forEach(card => {
        card.classList.remove("border-[#923826]", "bg-[#fbf9f5]", "ring-2", "ring-[#923826]/30");
        const badge = card.querySelector(".ts-badge");
        if (badge) {
          badge.classList.remove("bg-[#923826]", "text-white");
        }
      });

      if (el) {
        el.classList.add("border-[#923826]", "bg-[#fbf9f5]", "ring-2", "ring-[#923826]/30");
        const activeBadge = el.querySelector(".ts-badge");
        if (activeBadge) {
          activeBadge.classList.add("bg-[#923826]", "text-white");
        }
      }
    }

    // ✨ Gemini AI 타임스탬프 분석 및 재분석
    async function refreshAiTimestamps() {
      if (!currentVideo) {
        alert("먼저 영상을 상단에 입력하거나 좌측 샘플을 선택해 주세요.");
        return;
      }

      const loadingEl = document.getElementById("ts-loading");
      const listEl = document.getElementById("ts-items-list");
      const emptyEl = document.getElementById("ts-empty-state");
      const refreshBtn = document.getElementById("btn-refresh-ts");

      loadingEl.classList.remove("hidden");
      listEl.classList.add("opacity-40");
      refreshBtn.disabled = true;

      // 상단 프로그레스 바 가동 (오버레이 없이 상단 바만)
      ProgressController.start("AI 타임스탬프 분석 중", "자막의 핵심 맥락을 분석하고 있습니다...", false);

      const apiKey = localStorage.getItem("GEMINI_API_KEY") || "";

      try {
        const res = await fetch("/api/timestamps", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            video_info: currentVideo,
            api_key: apiKey
          })
        });
        const resData = await res.json();
        if (res.ok && resData.timestamps && resData.timestamps.length > 0) {
          saveStoredTimestamps(currentVideo.id, resData.timestamps);
          renderTimestamps(resData.timestamps);
        } else {
          alert("타임스탬프를 분석하지 못했습니다.");
        }
        ProgressController.finish(true);
      } catch (err) {
        ProgressController.finish(false);
        alert("타임스탬프 로드 오류: " + err.message);
      } finally {
        loadingEl.classList.add("hidden");
        listEl.classList.remove("opacity-40");
        refreshBtn.disabled = false;
      }
    }

    // 탭 전환 (AI 대화 / 타임스탬프)
    function switchRightTab(tab) {
      const btnChat = document.getElementById("tab-btn-chat");
      const btnTs = document.getElementById("tab-btn-timestamps");
      const panelChat = document.getElementById("tab-panel-chat");
      const panelTs = document.getElementById("tab-panel-timestamps");

      if (tab === "chat") {
        btnChat.className = "flex-1 py-3 text-center bg-[#f4f1ea] border-r border-[#e5dfd4] text-[#1c1917] font-bold transition";
        btnTs.className = "flex-1 py-3 text-center text-[#8a8376] hover:text-[#1c1917] transition flex items-center justify-center gap-1.5";
        panelChat.classList.remove("hidden");
        panelTs.classList.add("hidden");
      } else {
        btnTs.className = "flex-1 py-3 text-center bg-[#f4f1ea] border-l border-[#e5dfd4] text-[#1c1917] font-bold transition flex items-center justify-center gap-1.5";
        btnChat.className = "flex-1 py-3 text-center text-[#8a8376] hover:text-[#1c1917] transition";
        panelTs.classList.remove("hidden");
        panelChat.classList.add("hidden");

        // 만약 영상이 있는데 아직 타임스탬프가 없으면 자동 분석
        if (currentVideo && (!currentTimestamps || currentTimestamps.length === 0)) {
          if (SAMPLE_TIMESTAMPS[currentVideo.id]) {
            renderTimestamps(SAMPLE_TIMESTAMPS[currentVideo.id]);
          } else {
            refreshAiTimestamps();
          }
        }
      }
    }

    // 🔙 브라우저 뒤로가기 / 앞으로가기 완벽 동기화 (영상 + 메타데이터 + AI 대화 + 타임스탬프)
    window.addEventListener("popstate", (e) => {
      const state = e.state;
      if (state && state.view === "workspace" && state.url) {
        // 이전 영상으로 이동 (히스토리 추가 적재 X)
        loadVideoFromUrl(state.url, false);
      } else if (state && state.view === "landing") {
        // 첫 화면(랜딩)으로 이동
        resetToLanding(false);
      } else {
        // 상태 객체가 없는 경우 URL 파라미터 기준 복원
        const params = new URLSearchParams(window.location.search);
        const vid = params.get("v");
        if (vid) {
          loadVideoFromUrl(`https://www.youtube.com/watch?v=${vid}`, false);
        } else {
          resetToLanding(false);
        }
      }
    });

    // 페이지 진입 시 URL 입력창 자동 포커스, 초기 상태 및 시청 기록 렌더링
    window.addEventListener("DOMContentLoaded", () => {
      renderWatchHistory();

      // 주소창에 ?v= 파라미터가 있는지 검사하여 초기 상태 설정
      const params = new URLSearchParams(window.location.search);
      const initialVid = params.get("v");
      if (initialVid) {
        const initialUrl = `https://www.youtube.com/watch?v=${initialVid}`;
        window.history.replaceState({ view: "workspace", url: initialUrl, videoId: initialVid }, "", window.location.href);
        loadVideoFromUrl(initialUrl, false);
      } else {
        window.history.replaceState({ view: "landing" }, "", window.location.pathname);
        const landingInput = document.getElementById("landing-url-input");
        if (landingInput) landingInput.focus();
      }
    });
