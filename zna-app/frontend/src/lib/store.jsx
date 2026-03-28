import { createContext, useContext, useReducer } from 'react'

const initialState = {
  parsedData: null,
  resume: null,
  coverLetter: null,
  atsResult: null,
  jobDescription: '',
  targetJobTitle: '',
  atsHistory: [],   // array of scores for the trend chart
}

function reducer(state, action) {
  switch (action.type) {
    case 'SET_PARSED':
      return { ...state, parsedData: action.payload }
    case 'SET_RESUME':
      return {
        ...state,
        resume: action.payload,
        atsHistory: [
          ...state.atsHistory.slice(-9),
          action.payload?.ats_score ?? 0,
        ],
      }
    case 'SET_COVER_LETTER':
      return { ...state, coverLetter: action.payload }
    case 'SET_ATS_RESULT':
      return {
        ...state,
        atsResult: action.payload,
        atsHistory: [
          ...state.atsHistory.slice(-9),
          action.payload?.overall_score ?? 0,
        ],
      }
    case 'SET_JOB_DESCRIPTION':
      return { ...state, jobDescription: action.payload }
    case 'SET_TARGET_TITLE':
      return { ...state, targetJobTitle: action.payload }
    case 'CLEAR_ALL':
      return initialState
    default:
      return state
  }
}

const StoreCtx = createContext(null)

export function StoreProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState)
  return <StoreCtx.Provider value={{ state, dispatch }}>{children}</StoreCtx.Provider>
}

export function useStore() {
  const ctx = useContext(StoreCtx)
  if (!ctx) throw new Error('useStore must be used inside StoreProvider')
  return ctx
}
